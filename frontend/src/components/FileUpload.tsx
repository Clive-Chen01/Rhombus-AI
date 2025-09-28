import { useRef, useState, DragEvent, ChangeEvent } from 'react'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'

type Props = {
    onUpload: (f: File) => void
    filename: string
}

const ACCEPT = '.csv,.xlsx,.xls'

export default function FileUpload({ onUpload, filename }: Props) {
    const inputRef = useRef<HTMLInputElement>(null)
    const [dragActive, setDragActive] = useState(false)
    const [error, setError] = useState<string>('')

    function handleFiles(files?: FileList | null) {
        setError('')
        const f = files?.[0]
        if (!f) return
        const ok = ACCEPT.split(',').some(ext => f.name.toLowerCase().endsWith(ext))
        if (!ok) {
            setError('Please upload a CSV or Excel file (.csv, .xlsx, .xls)')
            return
        }
        onUpload(f)
    }

    function onInputChange(e: ChangeEvent<HTMLInputElement>) {
        handleFiles(e.target.files)
        e.target.value = ''
    }

    function onDragOver(e: DragEvent) {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(true)
    }

    function onDragLeave(e: DragEvent) {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
    }

    function onDrop(e: DragEvent) {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        handleFiles(e.dataTransfer?.files)
    }

    return (
        <Paper
            variant="outlined"
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            sx={{
                p: 4,
                textAlign: 'center',
                borderStyle: 'dashed',
                cursor: 'pointer',
                transition: 'all .15s ease',
                borderColor: dragActive ? 'primary.main' : 'divider',
                bgcolor: dragActive ? 'action.hover' : 'background.paper',
                '&:hover': { bgcolor: 'action.hover' },
            }}
            role="button"
            aria-label="Upload file. Drag & drop or click to choose"
        >
            <Stack spacing={1} alignItems="center">
                <CloudUploadIcon color={dragActive ? 'primary' : 'action'} fontSize="large" />
                <Typography variant="subtitle1" fontWeight={600}>
                    Drag or click to upload
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Supported: .csv, .xlsx, .xls
                </Typography>
                {error && (
                    <Typography variant="body2" color="error">{error}</Typography>
                )}
                {filename && !error && (
                <Stack direction="row" alignItems="center" spacing={1} mt={0.5}>
                    <CheckCircleIcon color="success" fontSize="small" />
                    <Typography variant="body2" color="success.main">
                        Uploaded: {filename}
                    </Typography>
                </Stack>
                )}
            </Stack>

            <input
                ref={inputRef}
                type="file"
                accept={ACCEPT}
                hidden
                onChange={onInputChange}
            />
        </Paper>
    )
}
