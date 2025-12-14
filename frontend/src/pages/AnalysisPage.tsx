import { useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { useToast } from "../hooks/use-toast";
import { apiClient } from "../utils/api";
import type { FileWithPreview, AnalysisResponse } from "../types/api";
import { X, Upload, Image as ImageIcon } from "lucide-react";

function AnalysisPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [machineId, setMachineId] = useState("");
  const [notes, setNotes] = useState("");

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Filtrar apenas imagens
      const imageFiles = acceptedFiles.filter((file) =>
        file.type.startsWith("image/")
      );

      if (imageFiles.length === 0) {
        toast({
          title: "Erro",
          description: "Por favor, selecione apenas arquivos de imagem.",
          variant: "destructive",
        });
        return;
      }

      // Validar quantidade total (4-12 imagens)
      const totalFiles = files.length + imageFiles.length;
      if (totalFiles > 12) {
        toast({
          title: "Limite excedido",
          description: "Você pode adicionar no máximo 12 imagens.",
          variant: "destructive",
        });
        return;
      }

      // Criar previews para as imagens
      const filesWithPreview = imageFiles.map((file) => {
        const fileWithPreview: FileWithPreview = Object.assign(file, {
          preview: URL.createObjectURL(file),
        });
        return fileWithPreview;
      });

      setFiles((prev) => [...prev, ...filesWithPreview]);
    },
    [files.length, toast]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    },
    multiple: true,
  });

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    // Revogar URL do preview para liberar memória
    if (files[index].preview) {
      URL.revokeObjectURL(files[index].preview);
    }
    setFiles(newFiles);
  };

  const handleAnalyze = async () => {
    // Validar quantidade mínima
    if (files.length < 4) {
      toast({
        title: "Imagens insuficientes",
        description: "Por favor, adicione pelo menos 4 imagens para análise.",
        variant: "destructive",
      });
      return;
    }

    if (files.length > 12) {
      toast({
        title: "Muitas imagens",
        description: "Por favor, selecione no máximo 12 imagens.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const response: AnalysisResponse = await apiClient.analyzeImages(
        files,
        machineId || undefined,
        notes || undefined
      );

      // Salvar resultado no localStorage para a página de relatório
      localStorage.setItem("analysisResult", JSON.stringify(response));

      // Limpar previews
      files.forEach((file) => {
        if (file.preview) {
          URL.revokeObjectURL(file.preview);
        }
      });

      toast({
        title: "Análise concluída",
        description: "As imagens foram analisadas com sucesso!",
      });

      navigate("/relatorio");
    } catch (error: any) {
      console.error("Erro ao analisar imagens:", error);
      toast({
        title: "Erro na análise",
        description: error.message || "Ocorreu um erro ao analisar as imagens.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Limpar previews ao desmontar
  useEffect(() => {
    return () => {
      files.forEach((file) => {
        if (file.preview) {
          URL.revokeObjectURL(file.preview);
        }
      });
    };
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Análise de Imagens</CardTitle>
            <CardDescription>
              Faça upload de 4-12 imagens da máquina para análise
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Área de upload */}
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? "border-primary bg-primary/5"
                  : "border-muted-foreground/25 hover:border-primary/50"
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              {isDragActive ? (
                <p className="text-primary font-medium">
                  Solte as imagens aqui...
                </p>
              ) : (
                <>
                  <p className="text-muted-foreground mb-2">
                    Arraste e solte as imagens aqui ou clique para selecionar
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Formatos aceitos: PNG, JPG, JPEG, GIF, WEBP
                  </p>
                </>
              )}
            </div>

            {/* Contador de imagens */}
            <div className="text-sm text-muted-foreground text-center">
              {files.length} de 4-12 imagens selecionadas
              {files.length < 4 && (
                <span className="text-destructive ml-2">
                  (mínimo: 4 imagens)
                </span>
              )}
            </div>

            {/* Preview das imagens */}
            {files.length > 0 && (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="relative group aspect-square rounded-lg overflow-hidden border"
                  >
                    <img
                      src={file.preview}
                      alt={file.name}
                      className="w-full h-full object-cover"
                    />
                    <button
                      onClick={() => removeFile(index)}
                      className="absolute top-2 right-2 bg-destructive text-destructive-foreground rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      aria-label="Remover imagem"
                    >
                      <X className="h-4 w-4" />
                    </button>
                    <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs p-1 truncate">
                      {file.name}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Campos opcionais */}
            <div className="space-y-4 pt-4 border-t">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  ID da Máquina (opcional)
                </label>
                <input
                  type="text"
                  value={machineId}
                  onChange={(e) => setMachineId(e.target.value)}
                  placeholder="Ex: MAQ-001"
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Observações (opcional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Adicione observações sobre a máquina..."
                  rows={3}
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
            </div>

            {/* Botões */}
            <div className="flex gap-2 pt-4">
              <Button
                onClick={handleAnalyze}
                disabled={isLoading || files.length < 4 || files.length > 12}
                className="flex-1"
              >
                {isLoading ? "Analisando..." : "Iniciar Análise"}
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate("/")}
                disabled={isLoading}
              >
                Voltar
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default AnalysisPage;
