import { useState } from 'react'


export default function TransformForm({ onPreview, onSubmit, columns, pattern, explanation }: any) {
    const [nl, setNl] = useState('Find email addresses')
    const [replacement, setReplacement] = useState('REDACTED')
    const [selected, setSelected] = useState<string[]>([])
    const [applyPhone, setApplyPhone] = useState(false)
    const [applyDate, setApplyDate] = useState(false)


    return (
        <section>
            <h2>2) Natural language → Regex → Replace</h2>
            <div className="row">
                <input value={nl} onChange={e=>setNl(e.target.value)} placeholder="Describe the pattern (e.g., Find email addresses)" />
                <button onClick={()=>onPreview(nl)}>Preview Regex</button>
            </div>
            {pattern && (<p><b>Regex:</b> <code>{pattern}</code>{explanation? ` — ${explanation}`: ''}</p>)}


            <div className="row">
                <input value={replacement} onChange={e=>setReplacement(e.target.value)} placeholder="Replacement value" />
            </div>


            {columns.length>0 && (
                <div className="row">
                    <label>Target columns (optional):</label>
                    <select multiple value={selected} onChange={(e)=>{
                        const opts = Array.from(e.target.selectedOptions).map(o=>o.value)
                        setSelected(opts)
                    }}>
                        {columns.map((c:string)=> <option key={c} value={c}>{c}</option>)}
                    </select>
                </div>
            )}


            <div className="row">
                <label><input type="checkbox" checked={applyPhone} onChange={()=>setApplyPhone(v=>!v)} /> Normalize AU phones (+61)</label>
                <label><input type="checkbox" checked={applyDate} onChange={()=>setApplyDate(v=>!v)} /> Normalize dates (YYYY-MM-DD)</label>
            </div>


            <button onClick={()=> onSubmit({
                natural_language: nl,
                replacement,
                columns: selected,
                apply_phone_normalization: applyPhone,
                apply_date_normalization: applyDate,
            })}>Apply</button>
        </section>
    )
}