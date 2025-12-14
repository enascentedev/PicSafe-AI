// Utilitários de validação

export interface ValidationResult {
  isValid: boolean
  error?: string
}

const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const MIN_FILES = 1
const MAX_FILES = 20

export function validateFiles(files: File[]): ValidationResult {
  if (files.length < MIN_FILES) {
    return {
      isValid: false,
      error: `Selecione pelo menos ${MIN_FILES} imagem`,
    }
  }

  if (files.length > MAX_FILES) {
    return {
      isValid: false,
      error: `Máximo de ${MAX_FILES} imagens permitidas`,
    }
  }

  for (const file of files) {
    const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))

    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      return {
        isValid: false,
        error: `Tipo de arquivo não suportado: ${file.name}. Use apenas imagens JPG, PNG, BMP ou TIFF.`,
      }
    }

    if (file.size > MAX_FILE_SIZE) {
      return {
        isValid: false,
        error: `Arquivo muito grande: ${file.name}. Máximo de 10MB por arquivo.`,
      }
    }
  }

  return { isValid: true }
}

export function validateMachineId(machineId: string): ValidationResult {
  if (!machineId.trim()) {
    return { isValid: true } // Opcional
  }

  if (machineId.length > 50) {
    return {
      isValid: false,
      error: 'ID da máquina deve ter no máximo 50 caracteres',
    }
  }

  // Apenas letras, números, hífen e underscore
  const regex = /^[a-zA-Z0-9_-]+$/
  if (!regex.test(machineId)) {
    return {
      isValid: false,
      error: 'ID da máquina deve conter apenas letras, números, hífen e underscore',
    }
  }

  return { isValid: true }
}

export function validateNotes(notes: string): ValidationResult {
  if (notes.length > 500) {
    return {
      isValid: false,
      error: 'Notas devem ter no máximo 500 caracteres',
    }
  }

  return { isValid: true }
}
