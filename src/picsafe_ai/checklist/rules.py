"""Motor conservador e rastreável de pré-avaliação NR-12."""

from picsafe_ai.api.schemas import (
    BoundingBox,
    ChecklistItem,
    ChecklistStatus,
    Detection,
    DetectionClass,
    DetectorMetadata,
    DetectorMode,
    EvidenceReference,
    PendingPhoto,
)


class RulesEngine:
    """Avalia evidências sem inferir conformidade pela ausência."""

    def apply_rules(
        self,
        detections: list[Detection],
        detector: DetectorMetadata,
    ) -> tuple[list[ChecklistItem], list[PendingPhoto]]:
        """Aplica as regras e gera pendências de evidência."""
        checklist = [
            self._rule_exposed_part(detections, detector),
            self._rule_emergency_stop(detections, detector),
            self._rule_safety_sign(detections, detector),
        ]
        if detector.mode is DetectorMode.SIMULATED:
            for item in checklist:
                if item.status is ChecklistStatus.OK:
                    item.status = ChecklistStatus.DESCONHECIDO
                    item.notes = (
                        "Evidência simulada: o status não valida a condição "
                        "real da máquina"
                    )
        return checklist, self._pending_photos(checklist, detections)

    def _rule_exposed_part(
        self,
        detections: list[Detection],
        detector: DetectorMetadata,
    ) -> ChecklistItem:
        exposed = [
            item
            for item in detections
            if item.class_name is DetectionClass.EXPOSED_MOVING_PART
        ]
        guards = [
            item for item in detections if item.class_name is DetectionClass.GUARD
        ]
        if not exposed:
            return ChecklistItem(
                rule_id="R-001",
                description="Verificar partes móveis expostas e proteções",
                status=ChecklistStatus.DESCONHECIDO,
                notes="Não há evidência visual suficiente de partes móveis",
            )

        unprotected: list[Detection] = []
        protected_refs: list[Detection] = []
        for exposed_item in exposed:
            matching_guard = next(
                (
                    guard
                    for guard in guards
                    if guard.image_id == exposed_item.image_id
                    and self.bbox_iou(exposed_item.bbox, guard.bbox) > 0
                ),
                None,
            )
            if matching_guard is None:
                unprotected.append(exposed_item)
            else:
                protected_refs.extend([exposed_item, matching_guard])

        if unprotected:
            return ChecklistItem(
                rule_id="R-001",
                description="Verificar partes móveis expostas e proteções",
                status=ChecklistStatus.ATENCAO,
                evidence="Há evidência de parte móvel sem proteção associada",
                evidence_refs=self._references(unprotected, detector),
                notes="Requer inspeção presencial por profissional habilitado",
            )
        return ChecklistItem(
            rule_id="R-001",
            description="Verificar partes móveis expostas e proteções",
            status=ChecklistStatus.OK,
            evidence="Partes móveis protegidas nas evidências fornecidas",
            evidence_refs=self._references(protected_refs, detector),
        )

    def _rule_emergency_stop(
        self,
        detections: list[Detection],
        detector: DetectorMetadata,
    ) -> ChecklistItem:
        evidence = [
            item
            for item in detections
            if item.class_name is DetectionClass.EMERGENCY_STOP
        ]
        if not evidence:
            return ChecklistItem(
                rule_id="R-002",
                description="Verificar botão ou cabo de emergência",
                status=ChecklistStatus.DESCONHECIDO,
                notes="Botão de emergência não evidenciado nas imagens",
            )
        return ChecklistItem(
            rule_id="R-002",
            description="Verificar botão ou cabo de emergência",
            status=ChecklistStatus.OK,
            evidence="Há evidência visual de dispositivo de emergência",
            evidence_refs=self._references(evidence, detector),
        )

    def _rule_safety_sign(
        self,
        detections: list[Detection],
        detector: DetectorMetadata,
    ) -> ChecklistItem:
        evidence = [
            item for item in detections if item.class_name is DetectionClass.SAFETY_SIGN
        ]
        if not evidence:
            return ChecklistItem(
                rule_id="R-003",
                description="Verificar sinalização de segurança",
                status=ChecklistStatus.DESCONHECIDO,
                notes="Sinalização não evidenciada nas imagens",
            )
        return ChecklistItem(
            rule_id="R-003",
            description="Verificar sinalização de segurança",
            status=ChecklistStatus.OK,
            evidence="Há evidência visual de sinalização",
            evidence_refs=self._references(evidence, detector),
        )

    def _pending_photos(
        self,
        checklist: list[ChecklistItem],
        detections: list[Detection],
    ) -> list[PendingPhoto]:
        pending: list[PendingPhoto] = []
        by_rule = {item.rule_id: item for item in checklist}
        if by_rule["R-002"].status is ChecklistStatus.DESCONHECIDO:
            pending.append(
                PendingPhoto(
                    description="Foto do posto de operação e painel de controle",
                    reason="Dispositivo de emergência não evidenciado",
                )
            )
        if by_rule["R-003"].status is ChecklistStatus.DESCONHECIDO:
            pending.append(
                PendingPhoto(
                    description="Foto dos pontos de acesso à zona perigosa",
                    reason="Sinalização de segurança não evidenciada",
                )
            )
        danger_zones = [
            item
            for item in detections
            if item.class_name is DetectionClass.DANGER_ZONE_OPENING
        ]
        signs = [
            item for item in detections if item.class_name is DetectionClass.SAFETY_SIGN
        ]
        for danger_zone in danger_zones:
            has_sign = any(
                sign.image_id == danger_zone.image_id
                and self.bbox_iou(danger_zone.bbox, sign.bbox) > 0.1
                for sign in signs
            )
            if not has_sign:
                pending.append(
                    PendingPhoto(
                        description="Foto em close da abertura perigosa",
                        reason="Abertura sem sinalização associada na mesma imagem",
                        image_id=danger_zone.image_id,
                    )
                )
        return pending

    @staticmethod
    def _references(
        detections: list[Detection],
        detector: DetectorMetadata,
    ) -> list[EvidenceReference]:
        return [
            EvidenceReference(
                image_id=item.image_id,
                bbox=item.bbox,
                detector_name=detector.name,
                detector_version=detector.version,
                detector_mode=detector.mode,
                confidence=item.confidence,
            )
            for item in detections
        ]

    @staticmethod
    def bbox_iou(first: BoundingBox, second: BoundingBox) -> float:
        """Calcula IoU para associar evidências na mesma imagem."""
        x_left = max(first.x_min, second.x_min)
        y_top = max(first.y_min, second.y_min)
        x_right = min(first.x_max, second.x_max)
        y_bottom = min(first.y_max, second.y_max)
        if x_right <= x_left or y_bottom <= y_top:
            return 0.0
        intersection = (x_right - x_left) * (y_bottom - y_top)
        first_area = (first.x_max - first.x_min) * (first.y_max - first.y_min)
        second_area = (second.x_max - second.x_min) * (second.y_max - second.y_min)
        union = first_area + second_area - intersection
        return intersection / union if union > 0 else 0.0
