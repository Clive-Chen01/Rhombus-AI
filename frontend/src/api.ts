export type UploadApiResp = {
    filename?: string
    headers?: string[]
    columns?: string[]
    data?: any[][]
}

export async function apiUpload(file: File): Promise<UploadApiResp> {
    const fd = new FormData()
    fd.append('file', file)
    const r = await fetch('/api/upload', { method: 'POST', body: fd })
    if (!r.ok) throw new Error(await r.text())
    return r.json()
}


export type TransformApiResp = {
    intent?: string
    pattern?: string
    flags?: string[]
    columns?: string[]
    replacement?: string
    assumptions?: string[]
    stats?: { updated_rows?: number; updated_cells?: number }
    headers?: string[]
    data?: any[][]
}


export async function apiTransform(prompt: string): Promise<TransformApiResp> {
    const r = await fetch('/api/transform', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
    })
    if (!r.ok) throw new Error(await r.text())
    return r.json() as Promise<TransformApiResp>
}