// Utilitários de formatação para exibição

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function formatDateTime(isoString: string): string {
  try {
    const date = new Date(isoString)
    return date.toLocaleString('pt-BR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch {
    return isoString
  }
}

export function formatDuration(seconds: number): string {
  if (seconds < 1) return '< 1s'

  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)

  if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`
  }

  return `${remainingSeconds}s`
}

export function formatConfidence(confidence: number): string {
  return `${(confidence * 100).toFixed(1)}%`
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'OK':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'ATENÇÃO':
      return 'text-orange-600 bg-orange-50 border-orange-200'
    case 'DESCONHECIDO':
      return 'text-gray-600 bg-gray-50 border-gray-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

export function getStatusIcon(status: string): string {
  switch (status) {
    case 'OK':
      return '✅'
    case 'ATENÇÃO':
      return '⚠️'
    case 'DESCONHECIDO':
      return '❓'
    default:
      return '❓'
  }
}
