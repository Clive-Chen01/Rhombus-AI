export default function FileUpload({ onUpload, filename }: { onUpload: (f: File)=>void, filename: string }) {
    return (
        <section>
            <h2>1) Upload CSV / Excel</h2>
            <input type="file" accept=".csv,.xlsx,.xls" onChange={(e)=>{
                const f = e.target.files?.[0]; if (f) onUpload(f);
            }} />
            {filename && <p>Uploaded: <b>{filename}</b></p>}
        </section>
    )
}