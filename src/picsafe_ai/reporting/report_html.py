"""Geração de relatórios HTML para a triagem NR-12."""

import logging
from datetime import datetime
from typing import List

from jinja2 import Template

from ..api.schemas import AnalysisResponse, ChecklistItem, ChecklistStatus, Detection, PendingPhoto
from ..config import settings

logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """Gerador de relatórios HTML para análises de triagem."""

    @staticmethod
    def generate_report(response: AnalysisResponse) -> str:
        """
        Gera relatório HTML completo da análise.

        Args:
            response: Resposta da análise com todos os dados.

        Returns:
            String HTML do relatório.
        """
        template = Template(HTMLReportGenerator._get_html_template())

        # Preparar dados para o template
        context = {
            "machine_id": response.machine_id or "Não informado",
            "timestamp": HTMLReportGenerator._format_timestamp(response.analysis_timestamp),
            "model_version": response.model_version,
            "confidence_threshold": f"{response.confidence_threshold:.2f}",
            "processing_time": f"{response.processing_time_seconds:.2f}",
            "detections_count": len(response.detections),
            "checklist_items": response.checklist,
            "pending_photos": response.pending_photos,
            "checklist_stats": HTMLReportGenerator._calculate_checklist_stats(response.checklist),
            "generated_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        }

        html_content = template.render(**context)
        logger.info("Relatório HTML gerado com sucesso")
        return html_content

    @staticmethod
    def _calculate_checklist_stats(checklist: List[ChecklistItem]) -> dict:
        """
        Calcula estatísticas do checklist.

        Args:
            checklist: Lista de itens do checklist.

        Returns:
            Dicionário com estatísticas.
        """
        stats = {
            "total": len(checklist),
            "ok": 0,
            "atencao": 0,
            "desconhecido": 0,
        }

        for item in checklist:
            if item.status == ChecklistStatus.OK:
                stats["ok"] += 1
            elif item.status == ChecklistStatus.ATENCAO:
                stats["atencao"] += 1
            elif item.status == ChecklistStatus.DESCONHECIDO:
                stats["desconhecido"] += 1

        return stats

    @staticmethod
    def _format_timestamp(timestamp_str: str) -> str:
        """
        Formata timestamp para exibição.

        Args:
            timestamp_str: Timestamp em ISO 8601.

        Returns:
            Timestamp formatado para PT-BR.
        """
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            return timestamp_str

    @staticmethod
    def _get_html_template() -> str:
        """Retorna o template HTML do relatório."""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Triagem Visual NR-12 - PicSafe AI</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .warning-banner {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .ok { color: #28a745; }
        .atencao { color: #ffc107; }
        .desconhecido { color: #6c757d; }

        .section {
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }
        .section h2 {
            color: #495057;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .checklist-item {
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .checklist-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }
        .status-ok { background-color: #d4edda; color: #155724; }
        .status-atencao { background-color: #fff3cd; color: #856404; }
        .status-desconhecido { background-color: #e2e3e5; color: #383d41; }

        .evidence {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            font-size: 0.9em;
            margin-top: 10px;
        }
        .pending-photo {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 0 5px 5px 0;
        }
        .footer {
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }
        .rule-id {
            font-weight: bold;
            color: #495057;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ PicSafe AI</h1>
        <h2>Relatório de Triagem Visual NR-12</h2>
        <p>Pré-avaliação automatizada de segurança de máquinas</p>
    </div>

    <div class="warning-banner">
        <strong>⚠️ IMPORTANTE:</strong> Esta é uma <strong>pré-avaliação automatizada</strong> baseada em
        análise visual de imagens. Os resultados apresentados são indicativos e requerem
        <strong>validação por profissional habilitado</strong> (Engenheiro de Segurança) para emissão
        de laudo oficial. Esta ferramenta não substitui inspeção presencial, análise de circuitos
        de segurança ou documentação técnica.
    </div>

    <div class="section">
        <h2>📊 Informações da Análise</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
            <div><strong>ID da Máquina:</strong> {{ machine_id }}</div>
            <div><strong>Data/Hora da Análise:</strong> {{ timestamp }}</div>
            <div><strong>Versão do Modelo:</strong> {{ model_version }}</div>
            <div><strong>Threshold de Confiança:</strong> {{ confidence_threshold }}</div>
            <div><strong>Tempo de Processamento:</strong> {{ processing_time }}s</div>
            <div><strong>Objetos Detectados:</strong> {{ detections_count }}</div>
        </div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number ok">{{ checklist_stats.ok }}</div>
            <div>Itens OK</div>
        </div>
        <div class="stat-card">
            <div class="stat-number atencao">{{ checklist_stats.atencao }}</div>
            <div>Itens ATENÇÃO</div>
        </div>
        <div class="stat-card">
            <div class="stat-number desconhecido">{{ checklist_stats.desconhecido }}</div>
            <div>Itens DESCONHECIDO</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ checklist_stats.total }}</div>
            <div>Total de Itens</div>
        </div>
    </div>

    <div class="section">
        <h2>📋 Checklist de Triagem</h2>
        {% for item in checklist_items %}
        <div class="checklist-item">
            <div class="checklist-header">
                <span class="rule-id">{{ item.rule_id }}</span>
                <span class="status-badge status-{{ item.status.lower() }}">{{ item.status }}</span>
            </div>
            <div>{{ item.description }}</div>
            {% if item.evidence %}
            <div class="evidence">
                <strong>Evidência:</strong> {{ item.evidence }}
            </div>
            {% endif %}
            {% if item.notes %}
            <div style="margin-top: 10px; font-style: italic; color: #6c757d;">
                {{ item.notes }}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>

    {% if pending_photos %}
    <div class="section">
        <h2>📸 Fotos Pendentes</h2>
        <p>As seguintes fotos são recomendadas para completar a avaliação:</p>
        {% for photo in pending_photos %}
        <div class="pending-photo">
            <strong>{{ photo.description }}</strong><br>
            <em>Motivo: {{ photo.reason }}</em>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="footer">
        <p>
            Relatório gerado por PicSafe AI em {{ generated_at }}<br>
            <strong>PicSafe AI v{{ model_version }} - PoC de Triagem Visual NR-12</strong>
        </p>
    </div>
</body>
</html>
        """.strip()
