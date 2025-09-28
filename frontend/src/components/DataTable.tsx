import Box from '@mui/material/Box'
import { DataGrid, GridColDef } from '@mui/x-data-grid'

type Props = { columns: string[]; rows: any[][] }

export default function DataTable({ columns, rows }: Props) {
    if (!columns?.length) return null

    const gridCols: GridColDef[] = columns.map((c) => ({
        field: c,
        headerName: c,
        flex: 1,
        minWidth: 120,
        sortable: false,
        headerClassName: 'dg-header',
    }))

    const gridRows = rows.map((r, i) => {
        const obj: any = { id: i + 1 }
        columns.forEach((c, idx) => (obj[c] = String(r[idx] ?? '')))
        return obj
    })

    return (
        <Box sx={{ width: '100%', height: 275 }}>
        <DataGrid
            rows={gridRows}
            columns={gridCols}
            density="compact"
            disableRowSelectionOnClick
            hideFooterSelectedRowCount
            pageSizeOptions={[5]}
            initialState={{ pagination: { paginationModel: { pageSize: 5, page: 0 } } }}
            sx={{
            width: '100%',
            '& .dg-header': { fontWeight: 700 },
            }}
        />
        </Box>
    )
}
