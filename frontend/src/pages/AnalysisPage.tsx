import { useCallback, useEffect, useRef, useState } from "react";
import { Upload, X } from "lucide-react";
import { useDropzone } from "react-dropzone";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { useToast } from "../hooks/use-toast";
import type { FileWithPreview } from "../types/api";
import { apiClient } from "../utils/api";
import { validateFiles, validateMetadata } from "../utils/validation";
import { navigate } from "../utils/navigation";

function AnalysisPage() {
  const { toast } = useToast();
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [machineId, setMachineId] = useState("");
  const [notes, setNotes] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const filesRef = useRef<FileWithPreview[]>([]);

  const onDrop = useCallback(
    (accepted: File[]) => {
      setFiles((current) => {
        if (current.length + accepted.length > 12) {
          toast({
            title: "Limite excedido",
            description: "Envie no máximo 12 imagens.",
            variant: "destructive",
          });
          return current;
        }
        return [
          ...current,
          ...accepted.map((file) =>
            Object.assign(file, { preview: URL.createObjectURL(file) }),
          ),
        ];
      });
    },
    [toast],
  );

  const dropzone = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
      "image/webp": [".webp"],
    },
    maxFiles: 12,
  });

  useEffect(() => {
    filesRef.current = files;
  }, [files]);

  useEffect(
    () => () =>
      filesRef.current.forEach((file) => URL.revokeObjectURL(file.preview)),
    [],
  );

  function removeFile(index: number) {
    setFiles((current) => {
      URL.revokeObjectURL(current[index].preview);
      return current.filter((_file, position) => position !== index);
    });
  }

  async function analyze() {
    const validation = validateFiles(files);
    const metadata = validateMetadata(machineId, notes);
    const error = validation.error || metadata.error;
    if (!validation.isValid || !metadata.isValid) {
      toast({ title: "Revise os dados", description: error, variant: "destructive" });
      return;
    }
    setIsLoading(true);
    try {
      const response = await apiClient.analyzeImages(
        files,
        machineId || undefined,
        notes || undefined,
      );
      sessionStorage.setItem("analysisResult", JSON.stringify(response));
      navigate("/relatorio");
    } catch (caught: unknown) {
      const message = caught instanceof Error ? caught.message : "Falha inesperada.";
      toast({ title: "Análise não concluída", description: message, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="container mx-auto max-w-4xl px-4 py-8">
      <Card>
        <CardHeader><CardTitle>Enviar evidências visuais</CardTitle></CardHeader>
        <CardContent className="space-y-5">
          <p className="text-sm text-muted-foreground">
            Envie de 4 a 12 imagens JPEG, PNG ou WebP. A PoC não emite laudo.
          </p>
          <div {...dropzone.getRootProps()} className="cursor-pointer rounded-lg border-2 border-dashed p-8 text-center">
            <input {...dropzone.getInputProps()} />
            <Upload className="mx-auto mb-2" />
            <p>Arraste as imagens ou clique para selecionar.</p>
          </div>
          <p>{files.length} imagem(ns) selecionada(s)</p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {files.map((file, index) => (
              <figure key={file.preview} className="relative">
                <img src={file.preview} alt="Prévia da evidência" className="aspect-square w-full rounded object-cover" />
                <button type="button" aria-label="Remover imagem" onClick={() => removeFile(index)} className="absolute right-1 top-1 rounded bg-red-700 p-1 text-white">
                  <X size={16} />
                </button>
              </figure>
            ))}
          </div>
          <label className="block">ID da máquina (opcional)
            <input value={machineId} maxLength={80} onChange={(event) => setMachineId(event.target.value)} className="mt-1 w-full rounded border p-2" />
          </label>
          <label className="block">Observações (opcional)
            <textarea value={notes} maxLength={500} onChange={(event) => setNotes(event.target.value)} className="mt-1 w-full rounded border p-2" />
          </label>
          <Button onClick={analyze} disabled={isLoading}>{isLoading ? "Analisando…" : "Iniciar pré-avaliação"}</Button>
        </CardContent>
      </Card>
    </main>
  );
}

export default AnalysisPage;
