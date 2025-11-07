from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
import secrets
from io import BytesIO
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str  # "teacher" or "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    full_name: str
    email: str
    role: str
    created_at: str

class CourseCreate(BaseModel):
    name: str
    code: str
    description: str
    academic_period: str

class Course(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    code: str
    description: str
    teacher_id: str
    academic_period: str
    access_code: str
    created_at: str

class EnrollmentCreate(BaseModel):
    access_code: str

class GradeInput(BaseModel):
    enrollment_id: str
    corte1: Optional[float] = None
    corte2: Optional[float] = None
    corte3: Optional[float] = None

class Grade(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    enrollment_id: str
    course_id: str
    student_id: str
    student_name: str
    corte1: Optional[float] = None
    corte2: Optional[float] = None
    corte3: Optional[float] = None
    final_grade: Optional[float] = None
    last_updated: str

class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    message: str
    type: str
    read: bool
    created_at: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def calculate_final_grade(corte1: Optional[float], corte2: Optional[float], corte3: Optional[float]) -> Optional[float]:
    if corte1 is not None and corte2 is not None and corte3 is not None:
        final = (corte1 * 0.3) + (corte2 * 0.35) + (corte3 * 0.35)
        return round(final, 2)
    return None

async def create_notification(user_id: str, message: str, notification_type: str):
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "message": message,
        "type": notification_type,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)

# Routes
@api_router.get("/")
async def root():
    return {"message": "Sistema de Gestión Académica API"}

# Auth routes
@api_router.post("/auth/register")
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # Validate role
    if user_data.role not in ["teacher", "student"]:
        raise HTTPException(status_code=400, detail="Rol inválido")
    
    # Create user
    user = {
        "id": str(uuid.uuid4()),
        "full_name": user_data.full_name,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "role": user_data.role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reset_token": None,
        "reset_token_expiry": None
    }
    
    await db.users.insert_one(user)
    
    # Create token
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@api_router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    user = await db.users.find_one({"email": request.email})
    if not user:
        # Don't reveal if email exists
        return {"message": "Si el correo existe, recibirás un enlace de recuperación"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    reset_token_expiry = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"reset_token": reset_token, "reset_token_expiry": reset_token_expiry}}
    )
    
    # In production, send email here
    # For now, return token for testing
    return {
        "message": "Si el correo existe, recibirás un enlace de recuperación",
        "reset_token": reset_token  # Remove in production
    }

@api_router.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    user = await db.users.find_one({"reset_token": request.token})
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido")
    
    # Check if token expired
    if user["reset_token_expiry"]:
        expiry = datetime.fromisoformat(user["reset_token_expiry"])
        if expiry < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Token expirado")
    
    # Update password
    new_password_hash = hash_password(request.new_password)
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"password_hash": new_password_hash, "reset_token": None, "reset_token_expiry": None}}
    )
    
    return {"message": "Contraseña actualizada exitosamente"}

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    return User(
        id=current_user["id"],
        full_name=current_user["full_name"],
        email=current_user["email"],
        role=current_user["role"],
        created_at=current_user["created_at"]
    )

# Course routes
@api_router.post("/courses", response_model=Course)
async def create_course(course_data: CourseCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Solo docentes pueden crear cursos")
    
    # Check if course code exists
    existing_course = await db.courses.find_one({"code": course_data.code})
    if existing_course:
        raise HTTPException(status_code=400, detail="El código del curso ya existe")
    
    course = {
        "id": str(uuid.uuid4()),
        "name": course_data.name,
        "code": course_data.code,
        "description": course_data.description,
        "teacher_id": current_user["id"],
        "academic_period": course_data.academic_period,
        "access_code": secrets.token_urlsafe(8),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.courses.insert_one(course)
    return Course(**course)

@api_router.get("/courses/teacher", response_model=List[Course])
async def get_teacher_courses(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Solo docentes")
    
    courses = await db.courses.find({"teacher_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    return [Course(**course) for course in courses]

@api_router.get("/courses/student", response_model=List[Course])
async def get_student_courses(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Solo estudiantes")
    
    # Get enrollments
    enrollments = await db.enrollments.find({"student_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    course_ids = [e["course_id"] for e in enrollments]
    
    if not course_ids:
        return []
    
    courses = await db.courses.find({"id": {"$in": course_ids}}, {"_id": 0}).to_list(1000)
    return [Course(**course) for course in courses]

@api_router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str, current_user: dict = Depends(get_current_user)):
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Check access
    if current_user["role"] == "teacher":
        if course["teacher_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="No autorizado")
    else:
        enrollment = await db.enrollments.find_one({
            "student_id": current_user["id"],
            "course_id": course_id
        })
        if not enrollment:
            raise HTTPException(status_code=403, detail="No inscrito en este curso")
    
    return Course(**course)

@api_router.put("/courses/{course_id}", response_model=Course)
async def update_course(course_id: str, course_data: CourseCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Solo docentes")
    
    course = await db.courses.find_one({"id": course_id})
    if not course or course["teacher_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    await db.courses.update_one(
        {"id": course_id},
        {"$set": {
            "name": course_data.name,
            "code": course_data.code,
            "description": course_data.description,
            "academic_period": course_data.academic_period
        }}
    )
    
    updated_course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    return Course(**updated_course)

@api_router.delete("/courses/{course_id}")
async def delete_course(course_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Solo docentes")
    
    course = await db.courses.find_one({"id": course_id})
    if not course or course["teacher_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Delete course, enrollments, and grades
    await db.courses.delete_one({"id": course_id})
    await db.enrollments.delete_many({"course_id": course_id})
    await db.grades.delete_many({"course_id": course_id})
    
    return {"message": "Curso eliminado"}

@api_router.post("/courses/enroll")
async def enroll_in_course(enrollment_data: EnrollmentCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Solo estudiantes")
    
    # Find course by access code
    course = await db.courses.find_one({"access_code": enrollment_data.access_code})
    if not course:
        raise HTTPException(status_code=404, detail="Código de acceso inválido")
    
    # Check if already enrolled
    existing_enrollment = await db.enrollments.find_one({
        "student_id": current_user["id"],
        "course_id": course["id"]
    })
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Ya estás inscrito en este curso")
    
    # Create enrollment
    enrollment = {
        "id": str(uuid.uuid4()),
        "student_id": current_user["id"],
        "course_id": course["id"],
        "enrolled_at": datetime.now(timezone.utc).isoformat()
    }
    await db.enrollments.insert_one(enrollment)
    
    # Create initial grade record
    grade = {
        "id": str(uuid.uuid4()),
        "enrollment_id": enrollment["id"],
        "course_id": course["id"],
        "student_id": current_user["id"],
        "student_name": current_user["full_name"],
        "corte1": None,
        "corte2": None,
        "corte3": None,
        "final_grade": None,
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
    await db.grades.insert_one(grade)
    
    return {"message": "Inscripción exitosa", "course": Course(**course)}

@api_router.get("/courses/{course_id}/students")
async def get_course_students(course_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Solo docentes")
    
    course = await db.courses.find_one({"id": course_id})
    if not course or course["teacher_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Get enrollments
    enrollments = await db.enrollments.find({"course_id": course_id}, {"_id": 0}).to_list(1000)
    student_ids = [e["student_id"] for e in enrollments]
    
    if not student_ids:
        return []
    
    # Get students
    students = await db.users.find(
        {"id": {"$in": student_ids}},
        {"_id": 0, "password_hash": 0, "reset_token": 0, "reset_token_expiry": 0}
    ).to_list(1000)
    
    return students

# Grade routes
@api_router.post("/grades")
async def create_or_update_grade(grade_data: GradeInput, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Solo docentes")
    
    # Validate grades
    for grade_value in [grade_data.corte1, grade_data.corte2, grade_data.corte3]:
        if grade_value is not None and (grade_value < 0 or grade_value > 5):
            raise HTTPException(status_code=400, detail="Las notas deben estar entre 0.0 y 5.0")
    
    # Get enrollment
    enrollment = await db.enrollments.find_one({"id": grade_data.enrollment_id})
    if not enrollment:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    
    # Check if teacher owns the course
    course = await db.courses.find_one({"id": enrollment["course_id"]})
    if not course or course["teacher_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Get existing grade
    existing_grade = await db.grades.find_one({"enrollment_id": grade_data.enrollment_id})
    
    # Prepare update
    update_data = {"last_updated": datetime.now(timezone.utc).isoformat()}
    if grade_data.corte1 is not None:
        update_data["corte1"] = grade_data.corte1
    if grade_data.corte2 is not None:
        update_data["corte2"] = grade_data.corte2
    if grade_data.corte3 is not None:
        update_data["corte3"] = grade_data.corte3
    
    # Calculate final grade
    corte1 = grade_data.corte1 if grade_data.corte1 is not None else existing_grade.get("corte1")
    corte2 = grade_data.corte2 if grade_data.corte2 is not None else existing_grade.get("corte2")
    corte3 = grade_data.corte3 if grade_data.corte3 is not None else existing_grade.get("corte3")
    
    final_grade = calculate_final_grade(corte1, corte2, corte3)
    if final_grade is not None:
        update_data["final_grade"] = final_grade
    
    await db.grades.update_one(
        {"enrollment_id": grade_data.enrollment_id},
        {"$set": update_data}
    )
    
    # Create notification for student
    background_tasks.add_task(
        create_notification,
        enrollment["student_id"],
        f"Nueva calificación registrada en {course['name']}",
        "grade_update"
    )
    
    updated_grade = await db.grades.find_one({"enrollment_id": grade_data.enrollment_id}, {"_id": 0})
    return Grade(**updated_grade)

@api_router.get("/grades/course/{course_id}", response_model=List[Grade])
async def get_course_grades(course_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Solo docentes")
    
    course = await db.courses.find_one({"id": course_id})
    if not course or course["teacher_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    grades = await db.grades.find({"course_id": course_id}, {"_id": 0}).to_list(1000)
    return [Grade(**grade) for grade in grades]

@api_router.get("/grades/student/course/{course_id}", response_model=Grade)
async def get_student_grade(course_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Solo estudiantes")
    
    grade = await db.grades.find_one({
        "course_id": course_id,
        "student_id": current_user["id"]
    }, {"_id": 0})
    
    if not grade:
        raise HTTPException(status_code=404, detail="Calificación no encontrada")
    
    return Grade(**grade)

@api_router.get("/grades/export/{course_id}")
async def export_grades_pdf(course_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Solo docentes")
    
    course = await db.courses.find_one({"id": course_id})
    if not course or course["teacher_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    grades = await db.grades.find({"course_id": course_id}, {"_id": 0}).to_list(1000)
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"<b>Reporte de Calificaciones</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Course info
    course_info = Paragraph(f"<b>Curso:</b> {course['name']} ({course['code']})<br/><b>Período:</b> {course['academic_period']}", styles['Normal'])
    elements.append(course_info)
    elements.append(Spacer(1, 12))
    
    # Table
    data = [['Estudiante', 'Corte 1 (30%)', 'Corte 2 (35%)', 'Corte 3 (35%)', 'Nota Final']]
    
    for grade in grades:
        row = [
            grade['student_name'],
            str(grade['corte1']) if grade['corte1'] is not None else '-',
            str(grade['corte2']) if grade['corte2'] is not None else '-',
            str(grade['corte3']) if grade['corte3'] is not None else '-',
            str(grade['final_grade']) if grade['final_grade'] is not None else '-'
        ]
        data.append(row)
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=calificaciones_{course['code']}.pdf"}
    )

# Notification routes
@api_router.get("/notifications", response_model=List[Notification])
async def get_notifications(current_user: dict = Depends(get_current_user)):
    notifications = await db.notifications.find(
        {"user_id": current_user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return [Notification(**notif) for notif in notifications]

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user["id"]},
        {"$set": {"read": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    return {"message": "Notificación marcada como leída"}

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()