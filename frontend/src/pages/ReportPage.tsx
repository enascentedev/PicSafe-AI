import { AlertCircle } from "lucide-react";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import type { AnalysisResponse } from "../types/api";
import { navigate } from "../utils/navigation";

function readResult(): AnalysisResponse | null {
  const saved = sessionStorage.getItem("analysisResult");
  if (!saved) return null;
  try {
    return JSON.parse(saved) as AnalysisResponse;
  } catch {
    sessionStorage.removeItem("analysisResult");
    return null;
  }
}

function ReportPage() {
  const result = readResult();
  if (!result) {
    return <main className="p-8"><p>Nenhuma análise disponível.</p><Button onClick={() => navigate("/analisar")}>Nova análise</Button></main>;
  }
  return (
    <main className="container mx-auto max-w-4xl space-y-5 px-4 py-8">
      <Card className="border-amber-500 bg-amber-50">
        <CardContent className="flex gap-3 pt-6"><AlertCircle /><p><strong>Pré-avaliação experimental.</strong> Não emite laudo, não declara conformidade NR-12 e requer validação por profissional habilitado.</p></CardContent>
      </Card>
      {result.detector.mode === "simulated" && (
        <Card className="border-red-600 bg-red-50"><CardContent className="pt-6"><strong>Detector simulado:</strong> as detecções não descrevem a máquina real.</CardContent></Card>
      )}
      {result.analysis_status === "partial" && (
        <Card className="border-amber-500"><CardContent className="pt-6">Resultado parcial: {result.image_errors.length} imagem(ns) falharam.</CardContent></Card>
      )}
      <Card><CardHeader><CardTitle>Checklist conservador</CardTitle></CardHeader><CardContent className="space-y-3">
        {result.checklist.map((item) => <article key={item.rule_id} className="rounded border p-3"><strong>{item.rule_id} — {item.status}</strong><p>{item.description}</p>{item.notes && <p className="text-sm">{item.notes}</p>}</article>)}
      </CardContent></Card>
      <Card><CardHeader><CardTitle>Relatório HTML isolado</CardTitle></CardHeader><CardContent>
        <iframe title="Relatório PicSafe" sandbox="" srcDoc={result.report_html} className="h-[650px] w-full border" />
      </CardContent></Card>
      <Button onClick={() => navigate("/analisar")}>Nova análise</Button>
    </main>
  );
}

export default ReportPage;
