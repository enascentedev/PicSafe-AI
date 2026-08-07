export type DetectionClass =
  | "emergency_stop"
  | "guard"
  | "exposed_moving_part"
  | "danger_zone_opening"
  | "safety_sign";

export type ChecklistStatus = "OK" | "ATENÇÃO" | "DESCONHECIDO";
export type DetectorMode = "real" | "simulated";
export type AnalysisStatus = "complete" | "partial";

export interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

export interface DetectorMetadata {
  name: string;
  version: string;
  mode: DetectorMode;
  configuration: Record<string, string>;
}

export interface Detection {
  class_name: DetectionClass;
  confidence: number;
  bbox: BoundingBox;
  image_id: string;
  image_path: string;
}

export interface EvidenceReference {
  image_id: string;
  bbox: BoundingBox;
  detector_name: string;
  detector_version: string;
  detector_mode: DetectorMode;
  confidence: number;
}

export interface ChecklistItem {
  rule_id: string;
  description: string;
  status: ChecklistStatus;
  evidence?: string;
  evidence_refs: EvidenceReference[];
  notes?: string;
}

export interface PendingPhoto {
  description: string;
  reason: string;
  image_id?: string;
}

export interface ImageProcessingError {
  image_id: string;
  code: string;
  message: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  analysis_status: AnalysisStatus;
  machine_id?: string;
  detections: Detection[];
  checklist: ChecklistItem[];
  pending_photos: PendingPhoto[];
  image_errors: ImageProcessingError[];
  detector: DetectorMetadata;
  report_html: string;
  model_version: string;
  confidence_threshold: number;
  thresholds: Record<string, number>;
  analysis_timestamp: string;
  processing_time_seconds: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  detector: DetectorMetadata;
  timestamp: string;
}

export interface FileWithPreview extends File {
  preview: string;
}
