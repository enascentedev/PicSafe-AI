// Tipos TypeScript correspondentes aos schemas Pydantic do backend

export type DetectionClass =
  | 'emergency_stop'
  | 'guard'
  | 'exposed_moving_part'
  | 'danger_zone_opening'
  | 'safety_sign'

export type ChecklistStatus = 'OK' | 'ATENÇÃO' | 'DESCONHECIDO'

export interface BoundingBox {
  x_min: number
  y_min: number
  x_max: number
  y_max: number
}

export interface Detection {
  class_name: DetectionClass
  confidence: number
  bbox: BoundingBox
  image_path: string
}

export interface ChecklistItem {
  rule_id: string
  description: string
  status: ChecklistStatus
  evidence?: string
  notes?: string
}

export interface PendingPhoto {
  description: string
  reason: string
}

export interface AnalysisRequest {
  machine_id?: string
  notes?: string
}

export interface AnalysisResponse {
  machine_id?: string
  detections: Detection[]
  checklist: ChecklistItem[]
  pending_photos: PendingPhoto[]
  report_html: string
  model_version: string
  confidence_threshold: number
  analysis_timestamp: string
  processing_time_seconds: number
}

export interface HealthResponse {
  status: string
  version: string
  model_version: string
  timestamp: string
}

// Tipos para o estado da aplicação
export interface AnalysisState {
  isLoading: boolean
  error: string | null
  result: AnalysisResponse | null
}

export interface FileWithPreview extends File {
  preview?: string
}
