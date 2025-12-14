import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";

function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>🛡️ PicSafe AI</CardTitle>
            <CardDescription>
              Triagem Visual de Segurança de Máquinas (NR-12)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Ferramenta de pré-avaliação automatizada baseada em imagens para
              acelerar a identificação de indícios de riscos relacionados à
              NR-12.
            </p>
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <p className="text-sm font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
                ⚠️ Importante
              </p>
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                Esta é uma pré-avaliação automatizada. Os resultados são
                indiciais e requerem validação por profissional habilitado
                (Engenheiro de Segurança).
              </p>
            </div>
            <Button
              onClick={() => navigate("/analisar")}
              className="w-full"
              size="lg"
            >
              Iniciar Análise
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default HomePage;
