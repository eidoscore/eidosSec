import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Loader2, Filter, Search } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'

export default function ScanDetails() {
    const { id } = useParams<{ id: string }>()
    const [progress, setProgress] = useState(0)
    const [logs, setLogs] = useState<string[]>([])

    // Finding Details Modal
    const [selectedFinding, setSelectedFinding] = useState<any>(null)
    const [isModalOpen, setIsModalOpen] = useState(false)

    // Fetch Scan Details
    const { data: scanData, isLoading: isScanLoading, refetch: refetchScan } = useQuery({
        queryKey: ['scan', id],
        queryFn: () => api.get(`/scans/${id}`) as Promise<any>,
        refetchInterval: (query) => {
            const data = query.state.data as any
            return data?.data?.status === 'in_progress' ? 1000 : false
        }
    })

    const scan = scanData?.data

    // Fetch Findings (only if completed)
    const { data: findingsData } = useQuery({
        queryKey: ['scan-findings', id],
        queryFn: () => api.get(`/scans/${id}/findings`) as Promise<any>,
        enabled: scan?.status === 'completed'
    })

    const findings = findingsData?.data?.items || []

    // WebSocket Connection
    useEffect(() => {
        if (!scan || scan.status !== 'in_progress') return

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${protocol}//${window.location.hostname}:8000/ws/scans/${id}` // Hardcoded port for dev

        const ws = new WebSocket(wsUrl)

        ws.onopen = () => {
            console.log('Connected to scan progress stream')
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                setProgress(data.progress)
                setLogs(prev => [...prev.slice(-4), data.message]) // Keep last 5 logs
                if (data.progress === 100) {
                    refetchScan()
                }
            } catch (e) {
                console.error('Failed to parse WS message', e)
            }
        }

        return () => {
            ws.close()
        }
    }, [id, scan?.status, refetchScan])

    const handleExport = async () => {
        try {
            const response = await api.get(`/scans/${id}/export`)
            const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `scan-${id}-findings.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Export failed', error)
            alert('Failed to export findings')
        }
    }

    if (isScanLoading) {
        return <div className="flex justify-center p-12"><Loader2 className="animate-spin h-8 w-8" /></div>
    }

    if (!scan) return <div>Scan not found</div>

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link to="/">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Scan Details</h1>
                    <p className="text-muted-foreground">
                        {scan.project_name || 'Project Scan'} • {new Date(scan.started_at).toLocaleString()}
                    </p>
                </div>
                <div className="ml-auto">
                    {scan.status === 'completed' && (
                        <div className="flex gap-2">
                            <Button onClick={handleExport} variant="outline">
                                Export JSON
                            </Button>
                        </div>
                    )}
                </div>
            </div>

            {/* Progress Section (if running) */}
            {(scan.status === 'in_progress' || scan.status === 'pending') && (
                <Card className="border-blue-500/20 bg-blue-500/5">
                    <CardHeader>
                        <CardTitle className="text-lg flex justify-between">
                            <span>Scan in Progress...</span>
                            <span>{progress}%</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <Progress value={progress} />
                        <div className="font-mono text-sm space-y-1 text-muted-foreground h-[120px] overflow-hidden bg-background/50 p-4 rounded-md border">
                            {logs.map((log, i) => (
                                <div key={i}>&gt; {log}</div>
                            ))}
                            {logs.length === 0 && <div>Waiting for scanner initialization...</div>}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Findings List (if completed) */}
            {scan.status === 'completed' && (
                <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-2xl font-bold">{scan.total_findings}</div>
                                <div className="text-sm text-muted-foreground">Total Findings</div>
                            </CardContent>
                        </Card>
                        {/* Summary placeholders - ideally we aggregate these from findings */}
                        <Card className="border-l-4 border-l-red-600">
                            <CardContent className="pt-6">
                                <div className="text-2xl font-bold text-red-600">
                                    {findings.filter((f: any) => f.severity === 'critical' || f.severity === 'high').length}
                                </div>
                                <div className="text-sm text-muted-foreground">Critical/High</div>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="flex items-center gap-4 py-4">
                        <div className="relative flex-1 max-w-sm">
                            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input placeholder="Search findings..." className="pl-8" />
                        </div>
                        <Button variant="outline">
                            <Filter className="mr-2 h-4 w-4" /> Filter
                        </Button>
                    </div>

                    <div className="border rounded-md">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Severity</TableHead>
                                    <TableHead>Type</TableHead>
                                    <TableHead>File</TableHead>
                                    <TableHead>Line</TableHead>
                                    <TableHead>Confidence</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {findings.map((finding: any) => (
                                    <TableRow
                                        key={finding.id}
                                        className="cursor-pointer hover:bg-muted/50"
                                        onClick={() => {
                                            setSelectedFinding(finding)
                                            setIsModalOpen(true)
                                        }}
                                    >
                                        <TableCell>
                                            <Badge variant={
                                                finding.severity === 'critical' ? 'destructive' :
                                                    finding.severity === 'high' ? 'destructive' :
                                                        finding.severity === 'medium' ? 'warning' : 'default'
                                            }>
                                                {finding.severity}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="font-medium">{finding.type}</TableCell>
                                        <TableCell className="font-mono text-xs text-muted-foreground">{finding.file_path}</TableCell>
                                        <TableCell>{finding.line_start}</TableCell>
                                        <TableCell>{finding.confidence}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </div>
            )}

            {/* Finding Detail Modal */}
            <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
                <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <Badge variant={
                                selectedFinding?.severity === 'critical' ? 'destructive' :
                                    selectedFinding?.severity === 'high' ? 'destructive' :
                                        selectedFinding?.severity === 'medium' ? 'warning' : 'default'
                            }>
                                {selectedFinding?.severity}
                            </Badge>
                            <span>{selectedFinding?.type}</span>
                        </DialogTitle>
                        <DialogDescription className="font-mono text-xs">
                            {selectedFinding?.file_path}:{selectedFinding?.line_start}
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-4">
                        <div>
                            <h4 className="font-medium mb-2">Description</h4>
                            <p className="text-sm text-muted-foreground">{selectedFinding?.message || 'No description provided.'}</p>
                        </div>

                        {selectedFinding?.code_snippet && (
                            <div>
                                <h4 className="font-medium mb-2">Code Snippet</h4>
                                <pre className="bg-muted p-4 rounded-md overflow-x-auto text-xs font-mono">
                                    {selectedFinding.code_snippet}
                                </pre>
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <h4 className="font-medium mb-1">CWE</h4>
                                <div className="text-sm">{selectedFinding?.cwe_id || 'N/A'}</div>
                            </div>
                            <div>
                                <h4 className="font-medium mb-1">OWASP</h4>
                                <div className="text-sm">{selectedFinding?.owasp_category || 'N/A'}</div>
                            </div>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>

        </div>
    )
}
