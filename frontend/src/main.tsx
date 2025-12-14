import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.tsx";
import "./index.css";

// #region agent log
// Log inicial
fetch("http://127.0.0.1:7242/ingest/89ffe1e0-8e76-499a-9621-30153b740b5b", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    location: "main.tsx:7",
    message: "main.tsx executando",
    data: {
      rootExists: !!document.getElementById("root"),
      url: window.location.href,
    },
    timestamp: Date.now(),
    sessionId: "debug-session",
    runId: "run2",
    hypothesisId: "A",
  }),
}).catch(() => {});

// Capturar erros de rede
window.addEventListener("error", (event) => {
  fetch("http://127.0.0.1:7242/ingest/89ffe1e0-8e76-499a-9621-30153b740b5b", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      location: "main.tsx:error-handler",
      message: "Erro capturado",
      data: {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      },
      timestamp: Date.now(),
      sessionId: "debug-session",
      runId: "run2",
      hypothesisId: "D",
    }),
  }).catch(() => {});
});

// Capturar erros de recursos não carregados
window.addEventListener("unhandledrejection", (event) => {
  fetch("http://127.0.0.1:7242/ingest/89ffe1e0-8e76-499a-9621-30153b740b5b", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      location: "main.tsx:rejection-handler",
      message: "Promise rejeitada",
      data: { reason: event.reason?.toString() },
      timestamp: Date.now(),
      sessionId: "debug-session",
      runId: "run2",
      hypothesisId: "D",
    }),
  }).catch(() => {});
});
// #endregion

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
