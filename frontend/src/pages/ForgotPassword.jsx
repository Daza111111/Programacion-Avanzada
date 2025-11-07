import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { api } from "@/App";
import { GraduationCap, Loader2, ArrowLeft } from "lucide-react";

export default function ForgotPassword() {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [resetToken, setResetToken] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await api.post("/auth/forgot-password", { email });
      toast.success("Enlace de recuperación enviado");
      // For demo purposes, show the token
      if (response.data.reset_token) {
        setResetToken(response.data.reset_token);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al enviar enlace");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-xl" data-testid="forgot-password-card">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-emerald-600 rounded-2xl flex items-center justify-center">
              <GraduationCap className="h-10 w-10 text-white" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold" style={{fontFamily: 'Space Grotesk, sans-serif'}}>Recuperar Contraseña</CardTitle>
          <CardDescription>Ingresa tu correo para recibir un enlace de recuperación</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Correo Electrónico</Label>
              <Input
                id="email"
                type="email"
                placeholder="correo@ejemplo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                data-testid="forgot-password-email-input"
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading} data-testid="forgot-password-submit-btn">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Enviando...
                </>
              ) : (
                "Enviar Enlace de Recuperación"
              )}
            </Button>
          </form>

          {resetToken && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg" data-testid="reset-token-display">
              <p className="text-sm font-semibold text-blue-900 mb-2">Token de prueba (solo para desarrollo):</p>
              <p className="text-xs text-blue-700 break-all mb-3">{resetToken}</p>
              <Link to={`/reset-password/${resetToken}`}>
                <Button variant="outline" size="sm" className="w-full" data-testid="use-reset-token-btn">
                  Usar este token para resetear
                </Button>
              </Link>
            </div>
          )}

          <div className="mt-6 text-center">
            <Link to="/login" className="inline-flex items-center text-sm text-blue-600 hover:underline" data-testid="back-to-login-link">
              <ArrowLeft className="mr-1 h-4 w-4" />
              Volver a iniciar sesión
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}