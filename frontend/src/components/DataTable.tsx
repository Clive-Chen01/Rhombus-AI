export default function DataTable({ columns, rows }: { columns: string[], rows: any[][] }) {
    if (!columns?.length) return null
    return (
        <section>
        <h2>3) Preview (first 100 rows)</h2>
        <div className="table-wrapper">
            <table>
                <thead>
                    <tr>{columns.map(c=> <th key={c}>{c}</th>)}</tr>
                </thead>
                <tbody>
                    {rows.map((r, i)=> (
                        <tr key={i}>{r.map((cell, j)=> <td key={j}>{String(cell ?? '')}</td>)}</tr>
                    ))}
                </tbody>
            </table>
        </div>
        </section>
    )
}