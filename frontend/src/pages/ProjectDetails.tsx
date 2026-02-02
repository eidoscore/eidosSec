import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, ArrowLeft, Play, Trash2, Calendar } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

export default function ProjectDetails() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const { data: projectData, isLoading } = useQuery({
        queryKey: ['project', id],
        queryFn: () => api.get(`/projects/${id}`),
    })

    const project = projectData?.data

    const startScanMutation = useMutation({
        mutationFn: () => api.post('/scans', { project_id: id, scan_type: 'full' }),
        onSuccess: (data: any) => {
            const scanId = data.data.id
            navigate(`/scans/${scanId}`)
        }
    })

    const deleteProjectMutation = useMutation({
        mutationFn: () => api.delete(`/projects/${id}`),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] })
            navigate('/')
        }
    })

    const handleDelete = () => {
        if (confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
            deleteProjectMutation.mutate()
        }
    }

    if (isLoading) return <div className="flex justify-center p-12"><Loader2 className="animate-spin" /></div>
    if (!project) return <div>Project not found</div>

    return (
        <div className="space-y-8">
            <div className="flex items-center gap-4">
                <Link to="/">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>
                    <p className="text-muted-foreground font-mono text-sm mt-1">{project.path}</p>
                </div>
                <div className="ml-auto flex gap-2">
                    <Button variant="destructive" size="icon" onClick={handleDelete} title="Delete Project">
                        <Trash2 className="h-4 w-4" />
                    </Button>
                    <Button onClick={() => startScanMutation.mutate()} disabled={startScanMutation.isPending}>
                        {startScanMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                        Start Scan
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium">Framework</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{project.framework || 'Unknown'}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium">Languages</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-wrap gap-2">
                            {project.languages?.map((l: string) => <Badge key={l} variant="secondary">{l}</Badge>)}
                            {(!project.languages || project.languages.length === 0) && <span className="text-muted-foreground">None detected</span>}
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm font-medium">Last Scan</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-muted-foreground">-</div>
                    </CardContent>
                </Card>
            </div>

            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <h2 className="text-xl font-bold">Scan History</h2>
                </div>

                {project.scans && project.scans.length > 0 ? (
                    <div className="border rounded-md">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Date</TableHead>
                                    <TableHead>Findings</TableHead>
                                    <TableHead>Duration</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {project.scans.map((scan: any) => (
                                    <TableRow key={scan.id}>
                                        <TableCell>
                                            <Badge variant={
                                                scan.status === 'completed' ? 'success' :
                                                    scan.status === 'failed' ? 'destructive' : 'secondary'
                                            }>
                                                {scan.status}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex items-center gap-2">
                                                <Calendar className="h-3 w-3 text-muted-foreground" />
                                                {new Date(scan.started_at).toLocaleDateString()}
                                                <span className="text-muted-foreground text-xs">{new Date(scan.started_at).toLocaleTimeString()}</span>
                                            </div>
                                        </TableCell>
                                        <TableCell>{scan.total_findings || '-'}</TableCell>
                                        <TableCell>{scan.execution_time ? `${scan.execution_time.toFixed(1)}s` : '-'}</TableCell>
                                        <TableCell className="text-right">
                                            <Button variant="outline" size="sm" asChild>
                                                <Link to={`/scans/${scan.id}`}>View Results</Link>
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                ) : (
                    <Card>
                        <CardContent className="py-12 text-center text-muted-foreground">
                            No scans performed yet. Click "Start Scan" to begin.
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    )
}
