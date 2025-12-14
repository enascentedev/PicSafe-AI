import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import type { AnalysisResponse, ChecklistStatus } from "../types/api";
import { AlertCircle, CheckCircle2, HelpCircle } from "lucide-react";

function ReportPage() {
  const navigate = useNavigate();
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(
    null
  );

  useEffect(() => {
    // Carregar resultado do localStorage
    const savedResult = localStorage.getItem("analysisResult");
    if (savedResult) {
      try {
        const result = JSON.parse(savedResult);
        setAnalysisResult(result);
      } catch (error) {
        console.error("Erro ao carregar resultado:", error);
      }
    }
  }, []);

  const getStatusIcon = (status: ChecklistStatus) => {
    switch (status) {
      case "OK":
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case "ATENÇÃO":
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      case "DESCONHECIDO":
        return <HelpCircle className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: ChecklistStatus) => {
    switch (status) {
      case "OK":
        return "bg-green-50 border-green-200 text-green-800";
      case "ATENÇÃO":
        return "bg-yellow-50 border-yellow-200 text-yellow-800";
      case "DESCONHECIDO":
        return "bg-gray-50 border-gray-200 text-gray-800";
    }
  };

  if (!analysisResult) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>Relatório de Análise</CardTitle>
              <CardDescription>Resultados da triagem visual</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground">
                Nenhum resultado de análise encontrado. Por favor, realize uma
                análise primeiro.
              </p>
              <div className="flex gap-2">
                <Button onClick={() => navigate("/analisar")}>
                  Nova Análise
                </Button>
                <Button variant="outline" onClick={() => navigate("/")}>
                  Voltar ao Início
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Aviso importante */}
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <p className="font-semibold text-yellow-800 mb-1">
                  ⚠️ Pré-avaliação Automatizada
                </p>
                <p className="text-sm text-yellow-700">
                  Este é um relatório de pré-avaliação automatizada baseada em
                  imagens. Os resultados são indiciais e requerem validação por
                  profissional habilitado (Engenheiro de Segurança) para emissão
                  de laudo oficial.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Informações da análise */}
        <Card>
          <CardHeader>
            <CardTitle>Informações da Análise</CardTitle>
            <CardDescription>
              Detalhes sobre a análise realizada
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {analysisResult.machine_id && (
              <div>
                <span className="font-medium">ID da Máquina: </span>
                <span>{analysisResult.machine_id}</span>
              </div>
            )}
            <div>
              <span className="font-medium">Data/Hora: </span>
              <span>
                {new Date(analysisResult.analysis_timestamp).toLocaleString(
                  "pt-BR"
                )}
              </span>
            </div>
            <div>
              <span className="font-medium">Tempo de processamento: </span>
              <span>{analysisResult.processing_time_seconds.toFixed(2)}s</span>
            </div>
            <div>
              <span className="font-medium">Versão do modelo: </span>
              <span>{analysisResult.model_version}</span>
            </div>
            <div>
              <span className="font-medium">Threshold de confiança: </span>
              <span>
                {(analysisResult.confidence_threshold * 100).toFixed(0)}%
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Detecções */}
        {analysisResult.detections.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>
                Detecções ({analysisResult.detections.length})
              </CardTitle>
              <CardDescription>Objetos detectados nas imagens</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {analysisResult.detections.map((detection, index) => (
                  <div
                    key={index}
                    className="p-3 border rounded-lg flex items-center justify-between"
                  >
                    <div>
                      <span className="font-medium capitalize">
                        {detection.class_name.replace("_", " ")}
                      </span>
                      <span className="text-sm text-muted-foreground ml-2">
                        {(detection.confidence * 100).toFixed(1)}% de confiança
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {detection.image_path}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Checklist */}
        {analysisResult.checklist.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>
                Checklist ({analysisResult.checklist.length} itens)
              </CardTitle>
              <CardDescription>Itens verificados na análise</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysisResult.checklist.map((item, index) => (
                  <div
                    key={index}
                    className={`p-4 border rounded-lg ${getStatusColor(
                      item.status
                    )}`}
                  >
                    <div className="flex items-start gap-3">
                      {getStatusIcon(item.status)}
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium">
                            {item.description}
                          </span>
                          <span className="text-sm font-semibold">
                            {item.status}
                          </span>
                        </div>
                        <div className="text-sm opacity-80">
                          <div>Regra: {item.rule_id}</div>
                          {item.evidence && (
                            <div className="mt-1">
                              Evidência: {item.evidence}
                            </div>
                          )}
                          {item.notes && (
                            <div className="mt-1">Notas: {item.notes}</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Pendências */}
        {analysisResult.pending_photos.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Pendências de Evidência</CardTitle>
              <CardDescription>Fotos adicionais recomendadas</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {analysisResult.pending_photos.map((pending, index) => (
                  <div key={index} className="p-3 border rounded-lg">
                    <div className="font-medium">{pending.description}</div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {pending.reason}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Relatório HTML (se disponível) */}
        {analysisResult.report_html && (
          <Card>
            <CardHeader>
              <CardTitle>Relatório Completo</CardTitle>
            </CardHeader>
            <CardContent>
              <div
                className="prose max-w-none"
                dangerouslySetInnerHTML={{ __html: analysisResult.report_html }}
              />
            </CardContent>
          </Card>
        )}

        {/* Botões de ação */}
        <div className="flex gap-2">
          <Button onClick={() => navigate("/analisar")}>Nova Análise</Button>
          <Button variant="outline" onClick={() => navigate("/")}>
            Voltar ao Início
          </Button>
        </div>
      </div>
    </div>
  );
}

export default ReportPage;
