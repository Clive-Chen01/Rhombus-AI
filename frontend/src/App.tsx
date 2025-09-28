import { useMemo, useState } from 'react'
import {
  ThemeProvider, createTheme, CssBaseline,
  AppBar, Toolbar, Typography, Container,
  Grid, Card, CardContent, IconButton, Box
} from '@mui/material'
import LightModeIcon from '@mui/icons-material/LightMode'
import DarkModeIcon from '@mui/icons-material/DarkMode'

import { apiTransform, TransformApiResp, apiUpload } from './api'
import FileUpload from './components/FileUpload'
import TransformForm from './components/TransformForm'
import DataTable from './components/DataTable'

export default function App() {
  const [mode, setMode] = useState<'light' | 'dark'>('light')

  const theme = useMemo(() => createTheme({
    palette: {
      mode,
      primary: { main: '#3949ab' },
      secondary: { main: '#00897b' }
    },
    shape: { borderRadius: 12 },
  }), [mode])

  const [columns, setColumns] = useState<string[]>([])
  const [rows, setRows] = useState<any[][]>([])
  const [pattern, setPattern] = useState<string>('')
  const [stats, setStats] = useState<{updated_rows?: number; updated_cells?: number}>({})

  const [filename, setFilename] = useState('')

  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string>('')

  async function handleUpload(file: File) {
    try {
      setLoading(true)
      const res = await apiUpload(file)

      const cols = res.headers ?? res.columns ?? []
      const data = res.data ?? []

      setColumns(cols)
      setRows(data)
      setFilename(res.filename || file.name)

      setPattern('')
      setStats({})
    } catch (e: any) {
      setErrorMsg(e?.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  async function handlePromptTransform(prompt: string): Promise<TransformApiResp> {
    try {
      setLoading(true)
      const resp = await apiTransform(prompt)

      setColumns(resp.headers ?? [])
      setRows(resp.data ?? [])
      setPattern(resp.pattern ?? '')
      setStats(resp.stats ?? {})

      return resp
    } catch (e: any) {
      setErrorMsg(e?.message || 'Transform failed')
      throw e
    } finally {
      setLoading(false)
    }
  }


  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="sticky" elevation={1}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
            Rhombus-AI
          </Typography>
          <IconButton color="inherit" onClick={() => setMode(m => m === 'light' ? 'dark' : 'light')}>
            {mode === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, md: 8 }}>
            <Card sx={{ height: { md: '100%' } }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  AI Modify File
                </Typography>
                <Box sx={{ width: 720 }}>
                    <TransformForm
                      onSubmit={(prompt) => handlePromptTransform(prompt)}
                      loading={loading}
                      hasFile={!!filename}
                      initialPattern={pattern}
                    />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 12, md: 4 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  File Upload
                </Typography>
                <FileUpload onUpload={handleUpload} filename={filename} />
              </CardContent>
            </Card>
          </Grid>

          {rows.length > 0 && (
            <Grid size={{ xs: 12 }}>
              <Card>
                <CardContent>
                  <Box sx={{ width: 1100, mx: 'auto' }}>
                    <DataTable columns={columns} rows={rows} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </Container>
    </ThemeProvider>
  )
}
