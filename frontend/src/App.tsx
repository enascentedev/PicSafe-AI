import { Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/toaster";
import HomePage from "./pages/HomePage";
import AnalysisPage from "./pages/AnalysisPage";
import ReportPage from "./pages/ReportPage";

function App() {
  // #region agent log
  fetch("http://127.0.0.1:7242/ingest/89ffe1e0-8e76-499a-9621-30153b740b5b", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      location: "App.tsx:9",
      message: "App renderizando",
      data: { pathname: window.location.pathname },
      timestamp: Date.now(),
      sessionId: "debug-session",
      runId: "run1",
      hypothesisId: "A",
    }),
  }).catch(() => {});
  // #endregion
  return (
    <div className="min-h-screen bg-background">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analisar" element={<AnalysisPage />} />
        <Route path="/relatorio" element={<ReportPage />} />
      </Routes>
      <Toaster />
    </div>
  );
}

export default App;
