
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { navigate } from "../utils/navigation";

function HomePage() {
  return (
    <main className="container mx-auto max-w-4xl px-4 py-8">
      <Card>
        <CardHeader><CardTitle>PicSafe AI</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <p>PoC de apoio à pré-avaliação visual de máquinas.</p>
          <div className="rounded border border-amber-500 bg-amber-50 p-4">
            Não emite laudo, não declara conformidade com a NR-12 e não substitui inspeção presencial por profissional habilitado.
          </div>
          <Button onClick={() => navigate("/analisar")}>Iniciar pré-avaliação</Button>
        </CardContent>
      </Card>
    </main>
  );
}

export default HomePage;
