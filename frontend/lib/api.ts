type ProgressCallback = (percent: number) => void

function apiBase() {
  // prefer explicit public env var; fall back to the dev proxy path
  return (process.env.NEXT_PUBLIC_API_BASE as string) ?? '/api/backend'
}

/**
 * Convert relative image paths to absolute URLs for backend
 */
export function getImageUrl(path: string): string {
  if (!path) return ''
  if (path.startsWith('http')) return path // already absolute
  const base = apiBase()
  return `${base}${path}`
}

export function analyzeImage(formData: FormData, opts?: { onProgress?: ProgressCallback; mode?: 'image' | 'video' }) {
  const mode = opts?.mode ?? 'image'
  const url = `${apiBase()}/api/${mode}/analyze`

  return new Promise<any>((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', url)

    xhr.onload = () => {
      const status = xhr.status
      const text = xhr.responseText
      if (status >= 200 && status < 300) {
        try {
          const json = JSON.parse(text || '{}')
          resolve(json)
        } catch (e) {
          resolve(text)
        }
      } else {
        reject(new Error(`Backend error: ${status} ${text}`))
      }
    }

    xhr.onerror = () => reject(new Error('Network error'))

    if (xhr.upload && opts?.onProgress) {
      xhr.upload.onprogress = (ev) => {
        if (ev.lengthComputable) {
          const percent = Math.round((ev.loaded / ev.total) * 100)
          opts.onProgress?.(percent)
        }
      }
    }

    xhr.send(formData)
  })
}

export async function health() {
  const res = await fetch(`${apiBase()}/health`)
  return res.ok
}
