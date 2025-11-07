import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { GraduationCap, BookOpen, Award, Users } from "lucide-react";

export default function Landing({ user }) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50">
      {/* Navbar */}
      <nav className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <GraduationCap className="h-8 w-8 text-blue-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent" style={{fontFamily: 'Space Grotesk, sans-serif'}}>AcademiCO</span>
            </div>
            <div className="flex items-center space-x-4">
              {user ? (
                <Button onClick={() => navigate("/dashboard")} data-testid="go-to-dashboard-btn">
                  Ir al Dashboard
                </Button>
              ) : (
                <>
                  <Button variant="ghost" onClick={() => navigate("/login")} data-testid="login-nav-btn">
                    Iniciar Sesión
                  </Button>
                  <Button onClick={() => navigate("/register")} data-testid="register-nav-btn">
                    Registrarse
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center space-y-8">
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900" style={{fontFamily: 'Space Grotesk, sans-serif'}}>
            Sistema de Gestión
            <span className="block mt-2 bg-gradient-to-r from-blue-600 to-emerald-600 bg-clip-text text-transparent">
              Académica Colombiana
            </span>
          </h1>
          <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto">
            Plataforma integral para docentes y estudiantes con gestión de cursos, calificaciones por cortes y reportes académicos del sistema educativo colombiano.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
            <Button
              size="lg"
              className="text-lg px-8 py-6"
              onClick={() => navigate("/register")}
              data-testid="get-started-btn"
            >
              Comenzar Ahora
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="text-lg px-8 py-6"
              onClick={() => navigate("/login")}
              data-testid="login-hero-btn"
            >
              Iniciar Sesión
            </Button>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mt-24">
          <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-lg transition-shadow" data-testid="feature-courses">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
              <BookOpen className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Gestión de Cursos</h3>
            <p className="text-gray-600">Crea y administra cursos con códigos de acceso únicos.</p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-lg transition-shadow" data-testid="feature-grades">
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4">
              <Award className="h-6 w-6 text-emerald-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Calificaciones por Cortes</h3>
            <p className="text-gray-600">Sistema de notas: Corte 1 (30%), Corte 2 (35%), Corte 3 (35%).</p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-lg transition-shadow" data-testid="feature-reports">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
              <Users className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Reportes PDF</h3>
            <p className="text-gray-600">Exporta reportes académicos en formato PDF.</p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-lg transition-shadow" data-testid="feature-notifications">
            <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center mb-4">
              <GraduationCap className="h-6 w-6 text-orange-600" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Notificaciones</h3>
            <p className="text-gray-600">Recibe alertas de nuevas calificaciones publicadas.</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t bg-white/50 backdrop-blur-sm mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-600">
            © 2025 AcademiCO - Sistema de Gestión Académica Colombiana
          </p>
        </div>
      </footer>
    </div>
  );
}