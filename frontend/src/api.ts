export async function apiUpload(file: File) {
    const fd = new FormData();
    fd.append('file', file);
    const r = await fetch('/api/upload', { method: 'POST', body: fd });
    if (!r.ok) throw new Error('Upload failed');
    return r.json();
}


export async function apiTransform(payload: any) {
    const r = await fetch('/api/transform', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!r.ok) throw new Error('Transform failed');
    return r.json();
}


export async function apiPreview(nl: string) {
    const r = await fetch('/api/llm-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ natural_language: nl }),
    });
    if (!r.ok) throw new Error('Preview failed');
    return r.json();
}