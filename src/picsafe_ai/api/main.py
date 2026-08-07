"""API FastAPI principal do PicSafe AI."""

import contextlib
import logging
import time
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from picsafe_ai.checklist import RulesEngine
from picsafe_ai.config import settings
from picsafe_ai.reporting import HTMLReportGenerator, ImageAnnotator
from picsafe_ai.utils import io as io_utils
from picsafe_ai.vision import PostProcessor, VisionDetector

from .schemas import AnalysisResponse

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Inicializar componentes
detector = VisionDetector()
post_processor = PostProcessor()
rules_engine = RulesEngine()

# Criar aplicação FastAPI
app = FastAPI(
    title="PicSafe AI - Triagem Visual NR-12",
    description="API para pré-avaliação visual de segurança de máquinas baseada em NR-12",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root() -> str:
    """Página inicial com informações sobre a API."""
    return """
    <html>
        <head>
            <title>PicSafe AI - Triagem Visual NR-12</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .header { text-align: center; color: #333; }
                .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🛡️ PicSafe AI</h1>
                <h2>PoC de Triagem Visual NR-12</h2>
                <p>Pré-avaliação automatizada de segurança de máquinas baseada em imagens</p>
            </div>

            <div class="warning">
                <strong>⚠️ IMPORTANTE:</strong> Esta é uma ferramenta de apoio para inspeções.
                Os resultados são indicativos e requerem validação por profissional habilitado.
            </div>

            <h3>Endpoints disponíveis:</h3>
            <ul>
                <li><code>GET /</code> - Esta página</li>
                <li><code>POST /v1/analisar</code> - Análise de imagens</li>
                <li><code>GET /docs</code> - Documentação interativa da API</li>
            </ul>

            <h3>Como usar:</h3>
            <ol>
                <li>Envie 4-12 fotos da máquina via POST para <code>/v1/analisar</code></li>
                <li>Receba relatório HTML com checklist preliminar</li>
                <li>Use profissional habilitado para validação final</li>
            </ol>
        </body>
    </html>
    """


@app.post("/v1/analisar", response_model=AnalysisResponse)
async def analisar_imagens(
    files: list[UploadFile] = File(...),
    machine_id: str = Form(None),
    notes: str = Form(None),
) -> AnalysisResponse:
    """
    Analisa imagens de máquina para triagem visual NR-12.

    Args:
        files: Lista de arquivos de imagem (4-12 recomendadas).
        machine_id: ID opcional da máquina analisada.
        notes: Notas adicionais sobre a análise.

    Returns:
        Análise completa com detecções, checklist e relatório.
    """
    start_time = time.time()

    try:
        # Validar entrada
        if len(files) < 1:
            raise HTTPException(
                status_code=400, detail="Pelo menos 1 imagem é necessária"
            )
        if len(files) > 20:
            raise HTTPException(
                status_code=400, detail="Máximo de 20 imagens permitidas"
            )

        logger.info(
            f"Iniciando análise de {len(files)} imagens para máquina {machine_id or 'não informada'}"
        )

        # Salvar imagens temporariamente
        saved_paths = []
        for file in files:
            if (
                not (file.filename or "")
                .lower()
                .endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff"))
            ):
                raise HTTPException(
                    status_code=400, detail=f"Formato não suportado: {file.filename}"
                )

            file_path = io_utils.save_uploaded_file(file, settings.uploads_dir)
            saved_paths.append(file_path)

        # Detectar objetos em todas as imagens
        all_detections = []
        for path in saved_paths:
            try:
                with open(path, "rb") as f:
                    image_bytes = f.read()

                detections = detector.predict(image_bytes, path)
                all_detections.extend(detections)

            except Exception as e:
                logger.exception(f"Erro ao processar {path}: {e}")
                continue

        # Pós-processamento das detecções
        processed_detections = post_processor.process_detections(all_detections)

        # Aplicar regras do checklist
        checklist_items, pending_photos = rules_engine.apply_rules(processed_detections)

        # Anotar imagens (opcional - para debug/visualização)
        annotated_paths = []
        for path in saved_paths:
            output_path = str(
                Path(settings.reports_dir) / f"annotated_{Path(path).name}"
            )
            annotated_path = ImageAnnotator.annotate_image(
                path, processed_detections, output_path
            )
            annotated_paths.append(annotated_path)

        # Gerar relatório HTML
        response = AnalysisResponse(
            machine_id=machine_id,
            detections=processed_detections,
            checklist=checklist_items,
            pending_photos=pending_photos,
            report_html="",  # Será preenchido abaixo
            model_version=settings.model_version,
            confidence_threshold=settings.confidence_threshold,
            analysis_timestamp=datetime.now().isoformat(),
            processing_time_seconds=time.time() - start_time,
        )

        response.report_html = HTMLReportGenerator.generate_report(response)

        # Salvar relatório em arquivo (opcional)
        report_filename = f"report_{machine_id or 'no_id'}_{int(time.time())}.html"
        report_path = settings.reports_dir / report_filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(response.report_html)

        logger.info(
            f"Análise concluída em {response.processing_time_seconds:.2f}s - {len(processed_detections)} detecções, {len(checklist_items)} itens no checklist"
        )

        # Limpar arquivos temporários (manter apenas relatório)
        for path in saved_paths:
            with contextlib.suppress(Exception):
                Path(path).unlink()

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro interno durante análise: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Endpoint de verificação de saúde da API."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "model_version": settings.model_version,
        "timestamp": datetime.now().isoformat(),
    }
