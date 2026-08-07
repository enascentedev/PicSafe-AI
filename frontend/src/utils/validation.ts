export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

const ALLOWED_MEDIA_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const MAX_FILE_SIZE = 10 * 1024 * 1024;
const MAX_REQUEST_SIZE = 60 * 1024 * 1024;
const MIN_FILES = 4;
const MAX_FILES = 12;

export function validateFiles(files: File[]): ValidationResult {
  if (files.length < MIN_FILES || files.length > MAX_FILES) {
    return { isValid: false, error: "Selecione entre 4 e 12 imagens." };
  }
  const total = files.reduce((size, file) => size + file.size, 0);
  if (total > MAX_REQUEST_SIZE) {
    return { isValid: false, error: "O conjunto excede o limite total de 60 MiB." };
  }
  for (const file of files) {
    if (!ALLOWED_MEDIA_TYPES.has(file.type)) {
      return { isValid: false, error: "Use somente JPEG, PNG ou WebP." };
    }
    if (file.size > MAX_FILE_SIZE) {
      return { isValid: false, error: "Cada imagem deve ter no máximo 10 MiB." };
    }
  }
  return { isValid: true };
}

export function validateMetadata(machineId: string, notes: string): ValidationResult {
  if (machineId.length > 80) {
    return { isValid: false, error: "O ID da máquina aceita até 80 caracteres." };
  }
  if (notes.length > 500) {
    return { isValid: false, error: "As observações aceitam até 500 caracteres." };
  }
  return { isValid: true };
}
