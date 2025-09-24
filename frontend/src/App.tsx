import { useState } from 'react'
import { apiUpload, apiTransform, apiPreview } from './api'
import FileUpload from './components/FileUpload'
import TransformForm from './components/TransformForm'
import DataTable from './components/DataTable'


export default function App() {
    const [columns, setColumns] = useState<string[]>([])
    const [rows, setRows] = useState<any[][]>([])
    const [filename, setFilename] = useState('')
    const [pattern, setPattern] = useState('')
    const [explanation, setExplanation] = useState<string | null>('')


    async function onUpload(file: File) {
        const res = await apiUpload(file)
        setColumns(res.columns)
        setRows(res.data)
        setFilename(res.filename)
    }


    async function onPreview(nl: string) {
        const res = await apiPreview(nl)
        setPattern(res.pattern)
        setExplanation(res.explanation)
    }


    async function onTransform(payload: any) {
        const res = await apiTransform(payload)
        setRows(res.data)
        setPattern(res.pattern)
        setExplanation(res.explanation)
    }


    return (
        <div className="container">
            <h1>Rhombus-AI</h1>
            <FileUpload onUpload={onUpload} filename={filename} />
            <TransformForm onPreview={onPreview} onSubmit={onTransform} columns={columns} pattern={pattern} explanation={explanation || ''} />
            <DataTable columns={columns} rows={rows} />
        </div>
    )
}