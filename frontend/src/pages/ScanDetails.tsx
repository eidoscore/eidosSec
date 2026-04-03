import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Loader2, Search, ShieldCheck, Lock, Sparkles } from 'lucide-react'
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
    const [toolStatuses, setToolStatuses] = useState<Record<string, { status: string, findings?: number }>>({})
    const [activeTools, setActiveTools] = useState<string[]>([])

    const [progress, setProgress] = useState(0)
    const [logs, setLogs] = useState<string[]>([])

    // Pagination & Filter State
    const [page, setPage] = useState(1)
    const pageSize = 50
    const [severityFilter, setSeverityFilter] = useState<string>('all')
    const [toolFilter, setToolFilter] = useState<string>('all')
    const [searchQuery, setSearchQuery] = useState('')

    // Finding Details Modal
    const [selectedFinding, setSelectedFinding] = useState<any>(null)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [isAnalyzing, setIsAnalyzing] = useState(false)

    // Fetch Scan Details
    const { data: scanData, isLoading: isScanLoading, refetch: refetchScan } = useQuery({
        queryKey: ['scan', id],
        queryFn: () => api.get(`/scans/${id}`) as Promise<any>,
        refetchInterval: (query) => {
            const data = query.state.data as any
            return data?.data?.status === 'running' ? 1000 : false
        }
    })

    const scan = scanData?.data

    // Fetch Findings (only if completed)
    const { data: findingsData } = useQuery({
        queryKey: ['scan-findings', id, page, severityFilter, toolFilter],
        queryFn: () => {
            let url = `/scans/${id}/findings?page=${page}&page_size=${pageSize}`
            if (severityFilter !== 'all') url += `&severity=${severityFilter}`
            if (toolFilter !== 'all') url += `&tool=${toolFilter}`
            return api.get(url) as Promise<any>
        },
        enabled: scan?.status === 'completed'
    })

    const findingsRaw = findingsData?.data?.items || []
    const totalFindings = findingsData?.data?.total || 0
    const totalPages = Math.ceil(totalFindings / pageSize)

    // Filter findings by search query locally
    const findings = findingsRaw.filter((finding: any) => {
        if (!searchQuery) return true
        const query = searchQuery.toLowerCase()
        return (
            finding.type.toLowerCase().includes(query) ||
            finding.message.toLowerCase().includes(query) ||
            finding.file_path.toLowerCase().includes(query)
        )
    })

    // WebSocket Connection
    useEffect(() => {
        if (!scan || scan.status !== 'running') return

        const token = localStorage.getItem('token')
        if (!token) return

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        // Use relative URL for WebSocket to avoid hardcoded ports
        const wsUrl = `${protocol}//${window.location.host}/ws/scans/${id}?token=${encodeURIComponent(token)}`

        const ws = new WebSocket(wsUrl)

        ws.onopen = () => {
            console.log('Connected to scan progress stream')
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                setProgress(data.progress)
                setLogs(prev => [...prev.slice(-4), data.message]) // Keep last 5 logs

                // valid fields: tools_list, current_tool, tool_status
                if (data.tools_list) {
                    setActiveTools(data.tools_list)
                    // Initialize statuses
                    const initialStatuses: any = {}
                    data.tools_list.forEach((t: string) => {
                        initialStatuses[t] = { status: 'pending' }
                    })
                    setToolStatuses(initialStatuses)
                }

                if (data.current_tool && data.tool_status) {
                    setToolStatuses(prev => ({
                        ...prev,
                        [data.current_tool]: {
                            status: data.tool_status,
                            findings: data.findings_count
                        }
                    }))
                }

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
    }, [id, scan, refetchScan])

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

    const handleCancel = async () => {
        if (!window.confirm('Are you sure you want to cancel this scan?')) return
        try {
            await api.post(`/scans/${id}/cancel`)
            refetchScan()
        } catch (error) {
            console.error('Cancel failed', error)
            alert('Failed to cancel scan')
        }
    }

    const handleAnalyze = async () => {
        if (!selectedFinding) return
        setIsAnalyzing(true)
        try {
            const response = await api.post(`/findings/${selectedFinding.id}/analyze`)
            setSelectedFinding(response.data)
        } catch (error) {
            console.error('Analysis failed', error)
            alert('AI Analysis failed. Please try again later.')
        } finally {
            setIsAnalyzing(false)
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
                    {(scan.status === 'running' || scan.status === 'pending') && (
                        <Button onClick={handleCancel} variant="destructive" size="sm">
                            Cancel Scan
                        </Button>
                    )}
                    {scan.status === 'completed' && (
                        <div className="flex gap-2">
                            <Button onClick={handleExport} variant="outline">
                                Export JSON
                            </Button>
                        </div>
                    )}
                </div>
            </div>
            {
                (scan.status === 'running' || scan.status === 'pending') && (
                    <div className="grid gap-6 md:grid-cols-2">
                        <Card className="border-blue-500/20 bg-blue-500/5">
                            <CardHeader>
                                <CardTitle className="text-lg flex justify-between">
                                    <span>Total Progress</span>
                                    <span>{progress}%</span>
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <Progress value={progress} />
                                <div className="font-mono text-xs space-y-1 text-muted-foreground h-[150px] overflow-hidden bg-background/50 p-4 rounded-md border">
                                    {logs.map((log, i) => (
                                        <div key={i}>&gt; {log}</div>
                                    ))}
                                    {logs.length === 0 && <div>Initializing scanner...</div>}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Active Tools</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {activeTools.length === 0 ? (
                                    <div className="text-sm text-muted-foreground flex items-center justify-center h-[150px]">
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Detecting environment...
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-2 gap-3">
                                        {activeTools.map(tool => {
                                            const state = toolStatuses[tool] || { status: 'pending' }
                                            return (
                                                <div key={tool} className="flex items-center justify-between p-2 border rounded-md text-sm bg-background/50">
                                                    <span className="font-medium">{tool}</span>
                                                    {state.status === 'pending' && <Badge variant="outline" className="text-xs text-muted-foreground">Pending</Badge>}
                                                    {state.status === 'running' && <Badge variant="secondary" className="text-xs animate-pulse">Running</Badge>}
                                                    {state.status === 'completed' && (
                                                        <Badge variant="default" className="text-xs bg-green-500 hover:bg-green-600">
                                                            {state.findings !== undefined ? `${state.findings} Found` : 'Done'}
                                                        </Badge>
                                                    )}
                                                    {state.status === 'failed' && <Badge variant="destructive" className="text-xs">Failed</Badge>}
                                                </div>
                                            )
                                        })}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                )
            }

            {/* Findings List (if completed) */}
            {
                scan.status === 'completed' && (
                    <div className="space-y-4">
                        {/* Zero Findings Celebration */}
                        {findings.length === 0 && (
                            <Card className="border-green-500/30 bg-green-500/5">
                                <CardContent className="py-12 text-center">
                                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/10 mb-4">
                                        <ShieldCheck className="h-8 w-8 text-green-600" />
                                    </div>
                                    <h3 className="text-xl font-semibold text-green-600 mb-2">
                                        No Vulnerabilities Found!
                                    </h3>
                                    <p className="text-muted-foreground max-w-md mx-auto mb-6">
                                        Great news! The Quick Scan didn't detect any security issues in your code.
                                        Consider running a Deep Scan for more comprehensive analysis.
                                    </p>
                                    <div className="flex items-center justify-center gap-3">
                                        <Button variant="outline" disabled className="opacity-60">
                                            <Lock className="mr-2 h-4 w-4" />
                                            Deep Scan (PRO)
                                        </Button>
                                        <span className="text-xs text-muted-foreground">
                                            Coming soon with 60+ security tools
                                        </span>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Stats Cards (only show if there are findings) */}
                        {findings.length > 0 && (
                            <>
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <Card>
                                        <CardContent className="pt-6">
                                            <div className="text-2xl font-bold">{scan.summary?.total_findings ?? totalFindings}</div>
                                            <div className="text-sm text-muted-foreground">Total Findings</div>
                                        </CardContent>
                                    </Card>
                                    <Card className="border-l-4 border-l-red-600">
                                        <CardContent className="pt-6">
                                            <div className="text-2xl font-bold text-red-600">
                                                {findings.filter((f: any) => f.severity === 'critical' || f.severity === 'high').length}
                                            </div>
                                            <div className="text-sm text-muted-foreground">Critical/High</div>
                                        </CardContent>
                                    </Card>
                                    <Card className="border-l-4 border-l-yellow-500">
                                        <CardContent className="pt-6">
                                            <div className="text-2xl font-bold text-yellow-600">
                                                {findings.filter((f: any) => f.severity === 'medium').length}
                                            </div>
                                            <div className="text-sm text-muted-foreground">Medium</div>
                                        </CardContent>
                                    </Card>
                                    <Card className="border-l-4 border-l-blue-500">
                                        <CardContent className="pt-6">
                                            <div className="text-2xl font-bold text-blue-600">
                                                {findings.filter((f: any) => f.severity === 'low' || f.severity === 'info').length}
                                            </div>
                                            <div className="text-sm text-muted-foreground">Low/Info</div>
                                        </CardContent>
                                    </Card>
                                </div>

                                <div className="flex flex-wrap items-center gap-3 py-4">
                                    <div className="relative flex-1 max-w-sm">
                                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                                        <Input 
                                            placeholder="Search findings..." 
                                            className="pl-8" 
                                            value={searchQuery}
                                            onChange={(e) => setSearchQuery(e.target.value)}
                                        />
                                    </div>
                                    
                                    <div className="flex items-center gap-2">
                                        <span className="text-sm font-medium text-muted-foreground">Severity:</span>
                                        <select 
                                            className="h-9 w-[120px] rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                                            value={severityFilter}
                                            onChange={(e) => {
                                                setSeverityFilter(e.target.value)
                                                setPage(1)
                                            }}
                                        >
                                            <option value="all">All</option>
                                            <option value="critical">Critical</option>
                                            <option value="high">High</option>
                                            <option value="medium">Medium</option>
                                            <option value="low">Low</option>
                                            <option value="info">Info</option>
                                        </select>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <span className="text-sm font-medium text-muted-foreground">Tool:</span>
                                        <select 
                                            className="h-9 w-[150px] rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                                            value={toolFilter}
                                            onChange={(e) => {
                                                setToolFilter(e.target.value)
                                                setPage(1)
                                            }}
                                        >
                                            <option value="all">All Tools</option>
                                            {scan.tools_executed?.map((tool: string) => (
                                                <option key={tool} value={tool}>{tool}</option>
                                            ))}
                                        </select>
                                    </div>

                                    {(severityFilter !== 'all' || toolFilter !== 'all' || searchQuery !== '') && (
                                        <Button 
                                            variant="ghost" 
                                            size="sm" 
                                            onClick={() => {
                                                setSeverityFilter('all')
                                                setToolFilter('all')
                                                setSearchQuery('')
                                                setPage(1)
                                            }}
                                            className="text-xs h-9"
                                        >
                                            Reset
                                        </Button>
                                    )}
                                </div>
                            </>
                        )}

                        {/* Findings Table (only show if there are findings) */}
                        {findings.length > 0 && (
                            <>
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
                                                        <Badge
                                                            variant={
                                                                finding.severity === 'critical' || finding.severity === 'high'
                                                                    ? 'destructive'
                                                                    : 'secondary'
                                                            }
                                                        >
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

                                {/* Pagination Controls */}
                                {totalPages > 1 && (
                                    <div className="flex items-center justify-between py-4">
                                        <div className="text-sm text-muted-foreground">
                                            Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, totalFindings)} of {totalFindings} findings
                                        </div>
                                        <div className="flex gap-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                                disabled={page === 1}
                                            >
                                                Previous
                                            </Button>
                                            <div className="flex items-center gap-1">
                                                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                                    // Simple pagination window logic
                                                    let pageNum = i + 1
                                                    if (totalPages > 5 && page > 3) {
                                                        pageNum = page - 3 + i
                                                        if (pageNum > totalPages) pageNum = totalPages - (4 - i)
                                                    }
                                                    if (pageNum <= 0) return null

                                                    return (
                                                        <Button
                                                            key={pageNum}
                                                            variant={page === pageNum ? "default" : "outline"}
                                                            size="sm"
                                                            className="w-8"
                                                            onClick={() => setPage(pageNum)}
                                                        >
                                                            {pageNum}
                                                        </Button>
                                                    )
                                                })}
                                            </div>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                                disabled={page === totalPages}
                                            >
                                                Next
                                            </Button>
                                        </div>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                )
            }

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
                                <h4 className="font-medium mb-1 text-sm">CWE</h4>
                                <div className="text-sm text-muted-foreground">{selectedFinding?.cwe_id || 'N/A'}</div>
                            </div>
                            <div>
                                <h4 className="font-medium mb-1 text-sm">OWASP</h4>
                                <div className="text-sm text-muted-foreground">{selectedFinding?.owasp_category || 'N/A'}</div>
                            </div>
                        </div>

                        <div className="pt-4 border-t">
                            <div className="flex items-center justify-between mb-4">
                                <h4 className="font-semibold flex items-center gap-2">
                                    <Sparkles className="h-4 w-4 text-blue-500" />
                                    AI Security Analysis
                                </h4>
                                {!selectedFinding?.ai_analysis?.analysis && (
                                    <Button
                                        size="sm"
                                        onClick={handleAnalyze}
                                        disabled={isAnalyzing}
                                    >
                                        {isAnalyzing ? (
                                            <>
                                                <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                                                Analyzing...
                                            </>
                                        ) : (
                                            'Generate Analysis'
                                        )}
                                    </Button>
                                )}
                            </div>

                            {selectedFinding?.ai_analysis?.analysis ? (
                                <div className="bg-blue-500/5 border border-blue-500/10 rounded-lg p-4 space-y-3">
                                    <div className="text-sm leading-relaxed whitespace-pre-wrap">
                                        {selectedFinding.ai_analysis.analysis}
                                    </div>
                                    {selectedFinding.ai_analysis.recommendation && (
                                        <div className="mt-4 p-3 bg-background rounded border border-blue-500/20">
                                            <h5 className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-1">Recommendation</h5>
                                            <p className="text-sm">{selectedFinding.ai_analysis.recommendation}</p>
                                        </div>
                                    )}
                                </div>
                            ) : !isAnalyzing && (
                                <div className="text-sm text-muted-foreground bg-muted/50 p-4 rounded-lg text-center">
                                    No AI analysis available for this finding yet.
                                </div>
                            )}

                            {isAnalyzing && (
                                <div className="space-y-3 animate-pulse">
                                    <div className="h-4 bg-muted rounded w-3/4"></div>
                                    <div className="h-4 bg-muted rounded w-full"></div>
                                    <div className="h-4 bg-muted rounded w-5/6"></div>
                                </div>
                            )}
                        </div>
                    </div>
                </DialogContent>
            </Dialog>

        </div >
    )
}
