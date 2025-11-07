import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { api } from "@/App";
import { GraduationCap, Plus, BookOpen, Users, Bell, LogOut, Download, Edit, Trash2, Copy, Loader2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";

export default function TeacherDashboard({ user, setUser }) {
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [students, setStudents] = useState([]);
  const [grades, setGrades] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [gradeDialogOpen, setGradeDialogOpen] = useState(false);
  const [selectedGrade, setSelectedGrade] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    code: "",
    description: "",
    academic_period: "",
  });
  const [gradeFormData, setGradeFormData] = useState({
    corte1: "",
    corte2: "",
    corte3: "",
  });

  useEffect(() => {
    loadCourses();
    loadNotifications();
  }, []);

  useEffect(() => {
    if (selectedCourse) {
      loadCourseDetails(selectedCourse.id);
    }
  }, [selectedCourse]);

  const loadCourses = async () => {
    try {
      const response = await api.get("/courses/teacher");
      setCourses(response.data);
    } catch (error) {
      toast.error("Error al cargar cursos");
    }
  };

  const loadCourseDetails = async (courseId) => {
    try {
      const [studentsRes, gradesRes] = await Promise.all([
        api.get(`/courses/${courseId}/students`),
        api.get(`/grades/course/${courseId}`),
      ]);
      setStudents(studentsRes.data);
      setGrades(gradesRes.data);
    } catch (error) {
      toast.error("Error al cargar detalles del curso");
    }
  };

  const loadNotifications = async () => {
    try {
      const response = await api.get("/notifications");
      setNotifications(response.data);
    } catch (error) {
      console.error("Error loading notifications");
    }
  };

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.post("/courses", formData);
      toast.success("Curso creado exitosamente");
      setCreateDialogOpen(false);
      setFormData({ name: "", code: "", description: "", academic_period: "" });
      loadCourses();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al crear curso");
    } finally {
      setLoading(false);
    }
  };

  const handleEditCourse = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.put(`/courses/${selectedCourse.id}`, formData);
      toast.success("Curso actualizado");
      setEditDialogOpen(false);
      loadCourses();
      const updatedCourse = courses.find(c => c.id === selectedCourse.id);
      if (updatedCourse) {
        setSelectedCourse({ ...updatedCourse, ...formData });
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al actualizar curso");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCourse = async (courseId) => {
    try {
      await api.delete(`/courses/${courseId}`);
      toast.success("Curso eliminado");
      loadCourses();
      if (selectedCourse?.id === courseId) {
        setSelectedCourse(null);
      }
    } catch (error) {
      toast.error("Error al eliminar curso");
    }
  };

  const handleUpdateGrade = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        enrollment_id: selectedGrade.enrollment_id,
      };
      if (gradeFormData.corte1) payload.corte1 = parseFloat(gradeFormData.corte1);
      if (gradeFormData.corte2) payload.corte2 = parseFloat(gradeFormData.corte2);
      if (gradeFormData.corte3) payload.corte3 = parseFloat(gradeFormData.corte3);

      await api.post("/grades", payload);
      toast.success("Calificación actualizada");
      setGradeDialogOpen(false);
      setGradeFormData({ corte1: "", corte2: "", corte3: "" });
      loadCourseDetails(selectedCourse.id);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al actualizar calificación");
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = async (courseId) => {
    try {
      const response = await api.get(`/grades/export/${courseId}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `calificaciones_${selectedCourse.code}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("Reporte descargado");
    } catch (error) {
      toast.error("Error al exportar reporte");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    navigate("/");
    toast.success("Sesión cerrada");
  };

  const copyAccessCode = (code) => {
    navigator.clipboard.writeText(code);
    toast.success("Código copiado al portapapeles");
  };

  const openEditDialog = (course) => {
    setSelectedCourse(course);
    setFormData({
      name: course.name,
      code: course.code,
      description: course.description,
      academic_period: course.academic_period,
    });
    setEditDialogOpen(true);
  };

  const openGradeDialog = (grade) => {
    setSelectedGrade(grade);
    setGradeFormData({
      corte1: grade.corte1 || "",
      corte2: grade.corte2 || "",
      corte3: grade.corte3 || "",
    });
    setGradeDialogOpen(true);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50">
      {/* Navbar */}
      <nav className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <GraduationCap className="h-8 w-8 text-blue-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent" style={{fontFamily: 'Space Grotesk, sans-serif'}}>AcademiCO</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Docente: <span className="font-semibold">{user.full_name}</span></span>
              <Button variant="ghost" size="sm" className="relative" data-testid="notifications-btn">
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs" data-testid="notification-badge">
                    {unreadCount}
                  </Badge>
                )}
              </Button>
              <Button variant="ghost" size="sm" onClick={handleLogout} data-testid="logout-btn">
                <LogOut className="h-5 w-5 mr-2" />
                Salir
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="courses" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 max-w-md">
            <TabsTrigger value="courses" data-testid="courses-tab">Mis Cursos</TabsTrigger>
            <TabsTrigger value="manage" data-testid="manage-tab">Gestionar Curso</TabsTrigger>
          </TabsList>

          {/* Courses Tab */}
          <TabsContent value="courses" className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-gray-900" style={{fontFamily: 'Space Grotesk, sans-serif'}}>Mis Cursos</h1>
                <p className="text-gray-600 mt-1">Gestiona tus cursos y estudiantes</p>
              </div>
              <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button data-testid="create-course-btn">
                    <Plus className="mr-2 h-4 w-4" />
                    Crear Curso
                  </Button>
                </DialogTrigger>
                <DialogContent data-testid="create-course-dialog">
                  <DialogHeader>
                    <DialogTitle>Crear Nuevo Curso</DialogTitle>
                    <DialogDescription>Completa los datos del curso</DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleCreateCourse} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Nombre del Curso</Label>
                      <Input
                        id="name"
                        placeholder="Ej: Matemáticas Avanzadas"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                        data-testid="course-name-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="code">Código del Curso</Label>
                      <Input
                        id="code"
                        placeholder="Ej: MAT301"
                        value={formData.code}
                        onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                        required
                        data-testid="course-code-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="description">Descripción</Label>
                      <Textarea
                        id="description"
                        placeholder="Descripción del curso"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        required
                        data-testid="course-description-input"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="academic_period">Período Académico</Label>
                      <Input
                        id="academic_period"
                        placeholder="Ej: 2025-1"
                        value={formData.academic_period}
                        onChange={(e) => setFormData({ ...formData, academic_period: e.target.value })}
                        required
                        data-testid="course-period-input"
                      />
                    </div>
                    <div className="flex space-x-2">
                      <Button type="submit" disabled={loading} data-testid="submit-create-course-btn">
                        {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Plus className="mr-2 h-4 w-4" />}
                        Crear Curso
                      </Button>
                      <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)} data-testid="cancel-create-course-btn">
                        Cancelar
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {courses.map((course) => (
                <Card key={course.id} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setSelectedCourse(course)} data-testid={`course-card-${course.code}`}>
                  <CardHeader>
                    <CardTitle className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <BookOpen className="h-5 w-5 text-blue-600" />
                          <span>{course.name}</span>
                        </div>
                        <Badge variant="outline" className="mt-2">{course.code}</Badge>
                      </div>
                    </CardTitle>
                    <CardDescription>{course.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <p className="text-gray-600"><span className="font-semibold">Período:</span> {course.academic_period}</p>
                      <div className="flex items-center justify-between pt-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={(e) => {
                            e.stopPropagation();
                            copyAccessCode(course.access_code);
                          }}
                          data-testid={`copy-code-btn-${course.code}`}
                        >
                          <Copy className="h-3 w-3 mr-1" />
                          {course.access_code}
                        </Button>
                        <div className="flex space-x-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={(e) => {
                              e.stopPropagation();
                              openEditDialog(course);
                            }}
                            data-testid={`edit-course-btn-${course.code}`}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={(e) => e.stopPropagation()}
                                data-testid={`delete-course-btn-${course.code}`}
                              >
                                <Trash2 className="h-4 w-4 text-red-600" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent data-testid="delete-course-dialog">
                              <AlertDialogHeader>
                                <AlertDialogTitle>¿Eliminar curso?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Esta acción eliminará el curso, inscripciones y calificaciones. No se puede deshacer.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel data-testid="cancel-delete-btn">Cancelar</AlertDialogCancel>
                                <AlertDialogAction onClick={() => handleDeleteCourse(course.id)} data-testid="confirm-delete-btn">
                                  Eliminar
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {courses.length === 0 && (
              <Card className="text-center py-12" data-testid="no-courses-message">
                <CardContent>
                  <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No tienes cursos creados aún</p>
                  <p className="text-sm text-gray-500 mt-2">Crea tu primer curso para comenzar</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Manage Course Tab */}
          <TabsContent value="manage" className="space-y-6">
            {selectedCourse ? (
              <>
                <div className="flex justify-between items-center">
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900" style={{fontFamily: 'Space Grotesk, sans-serif'}}>{selectedCourse.name}</h1>
                    <p className="text-gray-600 mt-1">{selectedCourse.code} - {selectedCourse.academic_period}</p>
                  </div>
                  <Button onClick={() => handleExportPDF(selectedCourse.id)} data-testid="export-pdf-btn">
                    <Download className="mr-2 h-4 w-4" />
                    Exportar PDF
                  </Button>
                </div>

                <Card data-testid="students-grades-card">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Users className="mr-2 h-5 w-5" />
                      Estudiantes y Calificaciones
                    </CardTitle>
                    <CardDescription>{students.length} estudiante(s) inscrito(s)</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {grades.length > 0 ? (
                      <div className="overflow-x-auto">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Estudiante</TableHead>
                              <TableHead className="text-center">Corte 1 (30%)</TableHead>
                              <TableHead className="text-center">Corte 2 (35%)</TableHead>
                              <TableHead className="text-center">Corte 3 (35%)</TableHead>
                              <TableHead className="text-center">Nota Final</TableHead>
                              <TableHead className="text-center">Acciones</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {grades.map((grade) => (
                              <TableRow key={grade.id} data-testid={`grade-row-${grade.student_name}`}>
                                <TableCell className="font-medium">{grade.student_name}</TableCell>
                                <TableCell className="text-center">{grade.corte1 !== null ? grade.corte1 : '-'}</TableCell>
                                <TableCell className="text-center">{grade.corte2 !== null ? grade.corte2 : '-'}</TableCell>
                                <TableCell className="text-center">{grade.corte3 !== null ? grade.corte3 : '-'}</TableCell>
                                <TableCell className="text-center">
                                  {grade.final_grade !== null ? (
                                    <Badge variant={grade.final_grade >= 3.0 ? "default" : "destructive"}>
                                      {grade.final_grade}
                                    </Badge>
                                  ) : '-'}
                                </TableCell>
                                <TableCell className="text-center">
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => openGradeDialog(grade)}
                                    data-testid={`edit-grade-btn-${grade.student_name}`}
                                  >
                                    <Edit className="h-4 w-4" />
                                  </Button>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500" data-testid="no-students-message">
                        No hay estudiantes inscritos en este curso
                      </div>
                    )}
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card className="text-center py-12" data-testid="select-course-message">
                <CardContent>
                  <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Selecciona un curso de la lista para gestionar</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Edit Course Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent data-testid="edit-course-dialog">
          <DialogHeader>
            <DialogTitle>Editar Curso</DialogTitle>
            <DialogDescription>Actualiza los datos del curso</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleEditCourse} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-name">Nombre del Curso</Label>
              <Input
                id="edit-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                data-testid="edit-course-name-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-code">Código del Curso</Label>
              <Input
                id="edit-code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                required
                data-testid="edit-course-code-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-description">Descripción</Label>
              <Textarea
                id="edit-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
                data-testid="edit-course-description-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-academic_period">Período Académico</Label>
              <Input
                id="edit-academic_period"
                value={formData.academic_period}
                onChange={(e) => setFormData({ ...formData, academic_period: e.target.value })}
                required
                data-testid="edit-course-period-input"
              />
            </div>
            <div className="flex space-x-2">
              <Button type="submit" disabled={loading} data-testid="submit-edit-course-btn">
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Actualizar
              </Button>
              <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)} data-testid="cancel-edit-course-btn">
                Cancelar
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Grade Dialog */}
      <Dialog open={gradeDialogOpen} onOpenChange={setGradeDialogOpen}>
        <DialogContent data-testid="grade-dialog">
          <DialogHeader>
            <DialogTitle>Actualizar Calificaciones</DialogTitle>
            <DialogDescription>
              Estudiante: {selectedGrade?.student_name}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUpdateGrade} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="corte1">Corte 1 (30%) - Escala 0.0 a 5.0</Label>
              <Input
                id="corte1"
                type="number"
                step="0.1"
                min="0"
                max="5"
                placeholder="Ej: 4.5"
                value={gradeFormData.corte1}
                onChange={(e) => setGradeFormData({ ...gradeFormData, corte1: e.target.value })}
                data-testid="grade-corte1-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="corte2">Corte 2 (35%) - Escala 0.0 a 5.0</Label>
              <Input
                id="corte2"
                type="number"
                step="0.1"
                min="0"
                max="5"
                placeholder="Ej: 4.2"
                value={gradeFormData.corte2}
                onChange={(e) => setGradeFormData({ ...gradeFormData, corte2: e.target.value })}
                data-testid="grade-corte2-input"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="corte3">Corte 3 (35%) - Escala 0.0 a 5.0</Label>
              <Input
                id="corte3"
                type="number"
                step="0.1"
                min="0"
                max="5"
                placeholder="Ej: 4.8"
                value={gradeFormData.corte3}
                onChange={(e) => setGradeFormData({ ...gradeFormData, corte3: e.target.value })}
                data-testid="grade-corte3-input"
              />
            </div>
            <div className="flex space-x-2">
              <Button type="submit" disabled={loading} data-testid="submit-grade-btn">
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Guardar Calificaciones
              </Button>
              <Button type="button" variant="outline" onClick={() => setGradeDialogOpen(false)} data-testid="cancel-grade-btn">
                Cancelar
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}