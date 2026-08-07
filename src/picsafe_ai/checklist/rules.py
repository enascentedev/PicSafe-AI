"""Motor de regras determinísticas para triagem NR-12."""

from picsafe_ai.api.schemas import (
    BoundingBox,
    ChecklistItem,
    ChecklistStatus,
    Detection,
    DetectionClass,
    PendingPhoto,
)


class RulesEngine:
    """Motor de regras para avaliação de conformidade NR-12 baseada em detecções."""

    @staticmethod
    def apply_rules(
        detections: list[Detection],
    ) -> tuple[list[ChecklistItem], list[PendingPhoto]]:
        """
        Aplica regras determinísticas às detecções encontradas.

        Args:
            detections: Lista de detecções nas imagens analisadas.

        Returns:
            Tupla com lista de itens do checklist e fotos pendentes.
        """
        checklist_items = []
        pending_photos = []

        # R-001: Parte móvel exposta sem proteção adequada
        checklist_items.append(RulesEngine._rule_r001_exposed_moving_part(detections))

        # R-002: Botão de emergência não evidenciado
        checklist_items.append(RulesEngine._rule_r002_emergency_stop(detections))

        # R-003: Verificar presença de sinalização de segurança
        checklist_items.append(RulesEngine._rule_r003_safety_signs(detections))

        # Adicionar pendências baseadas nas regras aplicadas
        pending_photos.extend(
            RulesEngine._generate_pending_photos(checklist_items, detections)
        )

        return checklist_items, pending_photos

    @staticmethod
    def _rule_r001_exposed_moving_part(detections: list[Detection]) -> ChecklistItem:
        """
        R-001: Parte móvel exposta presente e proteção ausente na região.

        Esta regra verifica se há partes móveis expostas sem proteção adequada.
        """
        exposed_parts = [
            d for d in detections if d.class_name == DetectionClass.EXPOSED_MOVING_PART
        ]
        guards = [d for d in detections if d.class_name == DetectionClass.GUARD]

        if not exposed_parts:
            # Não há partes móveis expostas detectadas - pode ser OK ou desconhecido
            return ChecklistItem(
                rule_id="R-001",
                description="Verificar se há partes móveis expostas sem proteção",
                status=ChecklistStatus.DESCONHECIDO,
                evidence=None,
                notes="Nenhuma parte móvel exposta detectada nas imagens fornecidas",
            )

        # Verificar se cada parte exposta tem proteção adequada
        unprotected_parts = []
        for exposed in exposed_parts:
            # Verificar se há guarda na mesma região (bounding box overlap)
            has_protection = any(
                RulesEngine._bboxes_overlap(exposed.bbox, guard.bbox)
                for guard in guards
            )
            if not has_protection:
                unprotected_parts.append(exposed)

        if unprotected_parts:
            evidence = f"Parte(s) móvel(is) exposta(s) sem proteção em {len(unprotected_parts)} local(is)"
            return ChecklistItem(
                rule_id="R-001",
                description="Verificar se há partes móveis expostas sem proteção",
                status=ChecklistStatus.ATENCAO,
                evidence=evidence,
                notes="Encontradas partes móveis expostas sem proteção adequada",
            )
        return ChecklistItem(
            rule_id="R-001",
            description="Verificar se há partes móveis expostas sem proteção",
            status=ChecklistStatus.OK,
            evidence="Todas as partes móveis expostas possuem proteção adequada",
            notes=None,
        )

    @staticmethod
    def _rule_r002_emergency_stop(detections: list[Detection]) -> ChecklistItem:
        """
        R-002: Botão/cabo de emergência não evidenciado em nenhuma imagem.

        Esta regra verifica se há botão de emergência visível nas imagens.
        """
        emergency_stops = [
            d for d in detections if d.class_name == DetectionClass.EMERGENCY_STOP
        ]

        if emergency_stops:
            evidence = f"Botão(ões) de emergência detectado(s) em {len(emergency_stops)} local(is)"
            return ChecklistItem(
                rule_id="R-002",
                description="Verificar presença de botão/cabo de emergência",
                status=ChecklistStatus.OK,
                evidence=evidence,
                notes=None,
            )
        return ChecklistItem(
            rule_id="R-002",
            description="Verificar presença de botão/cabo de emergência",
            status=ChecklistStatus.DESCONHECIDO,
            evidence=None,
            notes="Botão de emergência não detectado - necessário verificar posto de operação",
        )

    @staticmethod
    def _rule_r003_safety_signs(detections: list[Detection]) -> ChecklistItem:
        """
        R-003: Verificar presença de sinalização de segurança.

        Esta regra verifica se há sinalização de segurança adequada.
        """
        safety_signs = [
            d for d in detections if d.class_name == DetectionClass.SAFETY_SIGN
        ]

        if safety_signs:
            evidence = (
                f"Sinal(ais) de segurança detectado(s) em {len(safety_signs)} local(is)"
            )
            return ChecklistItem(
                rule_id="R-003",
                description="Verificar presença de sinalização de segurança",
                status=ChecklistStatus.OK,
                evidence=evidence,
                notes=None,
            )
        return ChecklistItem(
            rule_id="R-003",
            description="Verificar presença de sinalização de segurança",
            status=ChecklistStatus.DESCONHECIDO,
            evidence=None,
            notes="Sinalização de segurança não detectada nas imagens fornecidas",
        )

    @staticmethod
    def _generate_pending_photos(
        checklist_items: list[ChecklistItem], detections: list[Detection]
    ) -> list[PendingPhoto]:
        """
        Gera lista de fotos pendentes baseada nos itens do checklist.

        Args:
            checklist_items: Itens do checklist avaliados.
            detections: Detecções encontradas.

        Returns:
            Lista de fotos pendentes.
        """
        pending_photos = []

        # Se botão de emergência não foi detectado, pedir foto do posto de operação
        r002_item = next(
            (item for item in checklist_items if item.rule_id == "R-002"), None
        )
        if r002_item and r002_item.status == ChecklistStatus.DESCONHECIDO:
            pending_photos.append(
                PendingPhoto(
                    description="Foto do posto de operação/painel de controle",
                    reason="Botão de emergência não detectado - necessário verificar localização no posto de operação",
                )
            )

        # Se sinalização não foi detectada, pedir foto dos pontos de acesso
        r003_item = next(
            (item for item in checklist_items if item.rule_id == "R-003"), None
        )
        if r003_item and r003_item.status == ChecklistStatus.DESCONHECIDO:
            pending_photos.append(
                PendingPhoto(
                    description="Foto dos pontos de acesso à zona perigosa",
                    reason="Sinalização de segurança não detectada - necessário verificar sinalização nos pontos de acesso",
                )
            )

        # Verificar se há aberturas perigosas sem sinalização adequada
        danger_zones = [
            d for d in detections if d.class_name == DetectionClass.DANGER_ZONE_OPENING
        ]
        safety_signs = [
            d for d in detections if d.class_name == DetectionClass.SAFETY_SIGN
        ]

        for danger_zone in danger_zones:
            has_nearby_sign = any(
                RulesEngine._bboxes_overlap(danger_zone.bbox, sign.bbox, threshold=0.1)
                for sign in safety_signs
            )
            if not has_nearby_sign:
                pending_photos.append(
                    PendingPhoto(
                        description=f"Foto em close da abertura perigosa localizada em {danger_zone.image_path}",
                        reason="Abertura perigosa detectada sem sinalização próxima - necessário verificar sinalização específica",
                    )
                )

        return pending_photos

    @staticmethod
    def _bboxes_overlap(
        bbox1: "BoundingBox", bbox2: "BoundingBox", threshold: float = 0.0
    ) -> bool:
        """
        Verifica se dois bounding boxes se sobrepõem.

        Args:
            bbox1: Primeiro bounding box.
            bbox2: Segundo bounding box.
            threshold: Threshold mínimo de overlap (0-1).

        Returns:
            True se há overlap significativo.
        """
        # Calcular interseção
        x_left = max(bbox1.x_min, bbox2.x_min)
        y_top = max(bbox1.y_min, bbox2.y_min)
        x_right = min(bbox1.x_max, bbox2.x_max)
        y_bottom = min(bbox1.y_max, bbox2.y_max)

        if x_right <= x_left or y_bottom <= y_top:
            return False

        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        # Área dos bounding boxes
        bbox1_area = (bbox1.x_max - bbox1.x_min) * (bbox1.y_max - bbox1.y_min)
        bbox2_area = (bbox2.x_max - bbox2.x_min) * (bbox2.y_max - bbox2.y_min)

        # Calcular IoU (Intersection over Union)
        union_area = bbox1_area + bbox2_area - intersection_area
        iou = intersection_area / union_area if union_area > 0 else 0

        return iou > threshold
