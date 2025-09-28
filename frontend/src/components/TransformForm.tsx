import { useState, useEffect } from 'react'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import SendIcon from '@mui/icons-material/Send'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'

type ApiResp = {
  pattern?: string
  headers?: string[]
  data?: any[][]
}

type Props = {
  onSubmit: (prompt: string) => Promise<ApiResp>
  loading?: boolean
  hasFile?: boolean
  initialPattern?: string
}

export default function TransformForm({ onSubmit, loading = false, hasFile = false, initialPattern = '' }: Props) {
  const [prompt, setPrompt] = useState('')
  const [pattern, setPattern] = useState(initialPattern)

  useEffect(() => {
    setPattern(initialPattern)
  }, [initialPattern])

  async function handleSend() {
    const p = prompt.trim()
    if (!p) return
    try {
      const resp = await onSubmit(p)
      setPattern((resp?.pattern ?? '').trim())
    } catch {
    }
  }

  return (
    <Stack spacing={2}>
      <TextField
        fullWidth
        label="Prompt"
        placeholder="Please enter prompt"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        helperText="eg.: Normalize date to YYYY-MM-DD etc."
      />

      <Button
        variant="contained"
        startIcon={<SendIcon />}
        onClick={handleSend}
        disabled={!hasFile || loading || !prompt.trim()}
      >
        {loading ? 'Processing…' : 'Send'}
      </Button>

      {pattern && (
        <Stack spacing={1}>
          <Typography variant="subtitle1">Regex Use：</Typography>
          <Box
            component="pre"
            sx={{
              m: 0, p: 1, borderRadius: 1, bgcolor: 'action.hover',
              fontFamily:
                'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
              fontSize: 14, lineHeight: 1.6, whiteSpace: 'pre-wrap', wordBreak: 'break-all',
            }}
          >
            {pattern}
          </Box>
        </Stack>
      )}
    </Stack>
  )
}
