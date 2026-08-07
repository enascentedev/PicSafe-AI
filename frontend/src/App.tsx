import { useEffect, useState } from "react";

import { Toaster } from "./components/ui/toaster";
import AnalysisPage from "./pages/AnalysisPage";
import HomePage from "./pages/HomePage";
import ReportPage from "./pages/ReportPage";

function currentPage(pathname: string) {
  if (pathname === "/analisar") return <AnalysisPage />;
  if (pathname === "/relatorio") return <ReportPage />;
  return <HomePage />;
}

function App() {
  const [pathname, setPathname] = useState(window.location.pathname);
  useEffect(() => {
    const updatePath = () => setPathname(window.location.pathname);
    window.addEventListener("popstate", updatePath);
    return () => window.removeEventListener("popstate", updatePath);
  }, []);
  return (
    <div className="min-h-screen bg-background">
      {currentPage(pathname)}
      <Toaster />
    </div>
  );
}

export default App;
