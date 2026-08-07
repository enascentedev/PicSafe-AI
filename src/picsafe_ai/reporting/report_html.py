"""Relatório HTML seguro da pré-avaliação."""

from typing import ClassVar

from jinja2 import Environment, select_autoescape

from picsafe_ai.api.schemas import AnalysisResponse


class HTMLReportGenerator:
    """Gera HTML autoescapado e honesto sobre o modo do detector."""

    TEMPLATE: ClassVar[
        str
    ] = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pré-avaliação PicSafe</title>
  <style>
    body { font-family: sans-serif; margin: 2rem auto; max-width: 900px; color: #172033; }
    .banner { border: 2px solid #b45309; background: #fffbeb; padding: 1rem; }
    .simulated { border-color: #b91c1c; background: #fef2f2; }
    section { margin-top: 1.5rem; }
    article { border: 1px solid #cbd5e1; border-radius: .5rem; margin: .75rem 0; padding: 1rem; }
    dt { font-weight: 700; } dd { margin-bottom: .5rem; }
  </style>
</head>
<body>
  <h1>PicSafe — pré-avaliação visual</h1>
  <div class="banner{% if detector.mode.value == 'simulated' %} simulated{% endif %}">
    <strong>Pré-avaliação automatizada. Requer validação por profissional habilitado.</strong>
    <p>Detector: {{ detector.name }} {{ detector.version }} — modo {{ detector.mode.value }}.</p>
    {% if detector.mode.value == 'simulated' %}
    <p>As evidências e pontuações abaixo são simuladas. Não descrevem a máquina real.</p>
    {% endif %}
  </div>
  <dl>
    <dt>Análise</dt><dd>{{ analysis_id }}</dd>
    <dt>Máquina</dt><dd>{{ machine_id or 'Não informada' }}</dd>
    <dt>Estado</dt><dd>{{ analysis_status.value }}</dd>
    <dt>Horário</dt><dd>{{ analysis_timestamp }}</dd>
  </dl>
  <section>
    <h2>Checklist conservador</h2>
    {% for item in checklist %}
    <article>
      <strong>{{ item.rule_id }} — {{ item.status.value }}</strong>
      <p>{{ item.description }}</p>
      {% if item.evidence %}<p>Evidência: {{ item.evidence }}</p>{% endif %}
      {% if item.notes %}<p>Limitação: {{ item.notes }}</p>{% endif %}
      {% for reference in item.evidence_refs %}
      <p>Imagem {{ reference.image_id }}; confiança {{ '%.2f'|format(reference.confidence) }};
         detector {{ reference.detector_name }} ({{ reference.detector_mode.value }}).</p>
      {% endfor %}
    </article>
    {% endfor %}
  </section>
  {% if image_errors %}
  <section><h2>Falhas parciais</h2>
    {% for error in image_errors %}<p>{{ error.image_id }} — {{ error.message }}</p>{% endfor %}
  </section>
  {% endif %}
  <section><h2>Pendências de evidência</h2>
    {% for pending in pending_photos %}<p>{{ pending.description }} — {{ pending.reason }}</p>{% endfor %}
  </section>
  <p><strong>Limitações:</strong> esta PoC não emite laudo, não declara conformidade NR-12,
     não possui métricas reais e não substitui inspeção presencial.</p>
</body>
</html>
"""

    @classmethod
    def generate_report(cls, response: AnalysisResponse) -> str:
        """Renderiza todos os valores fornecidos com autoescape."""
        environment = Environment(
            autoescape=select_autoescape(default_for_string=True),
        )
        template = environment.from_string(cls.TEMPLATE)
        return template.render(**response.model_dump())
