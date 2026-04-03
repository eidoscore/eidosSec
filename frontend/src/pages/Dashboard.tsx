import { useQuery } from '@tanstack/react-query'
import { Loader2, Plus, ArrowRight } from 'lucide-react'
import { api } from '@/lib/api'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'

interface Project {
    id: string
    name: string
    path: string
    scans_count: number
    created_at: string
}

export default function Dashboard() {
    const { data: health, isLoading: healthLoading } = useQuery({
        queryKey: ['health'],
        queryFn: () => api.get('/health') as Promise<any>,
        refetchInterval: 30000,
    })

    const { data: projectsData, isLoading: projectsLoading } = useQuery({
        queryKey: ['projects'],
        queryFn: () => api.get('/projects') as Promise<any>,
    })
    
    const { data: scanStats, isLoading: statsLoading } = useQuery({
        queryKey: ['scan-stats'],
        queryFn: () => api.get('/scans/stats') as Promise<any>,
        refetchInterval: 10000,
    })

    const projects = projectsData?.data || []

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>
                    <p className="text-muted-foreground mt-2">
                        Overview of your security posture
                    </p>
                </div>
                <Link to="/projects/new">
                    <Button>
                        <Plus className="mr-2 h-4 w-4" /> New Project
                    </Button>
                </Link>
            </div>

            {/* System Status Card */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">System Status</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                            <span className="font-medium">Backend:</span>
                            {healthLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                            ) : health?.data?.status === 'healthy' ? (
                                <Badge variant="success">Healthy</Badge>
                            ) : (
                                <Badge variant="destructive">Unhealthy</Badge>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="font-medium">Database:</span>
                            {healthLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                            ) : health?.data?.database === 'connected' ? (
                                <Badge variant="success">Connected</Badge>
                            ) : (
                                <Badge variant="destructive">Disconnected</Badge>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="font-medium">Redis:</span>
                            {healthLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                            ) : health?.data?.redis === 'connected' ? (
                                <Badge variant="success">Connected</Badge>
                            ) : (
                                <Badge variant="destructive">Disconnected</Badge>
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Total Projects</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{projects.length}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Scans Completed</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {statsLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                scanStats?.data?.total_scans || 0
                            )}
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Active Scans</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {statsLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                scanStats?.data?.active_scans || 0
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Recent Projects */}
            <div className="space-y-4">
                <h2 className="text-2xl font-semibold tracking-tight">Recent Projects</h2>
                {projectsLoading ? (
                    <div className="flex justify-center p-8">
                        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                ) : projects.length === 0 ? (
                    <Card>
                        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                            <div className="rounded-full bg-primary/10 p-3 mb-4">
                                <Plus className="h-6 w-6 text-primary" />
                            </div>
                            <h3 className="text-lg font-semibold">No projects yet</h3>
                            <p className="text-muted-foreground mb-4 max-w-sm">
                                Get started by creating your first project to scan for vulnerabilities.
                            </p>
                            <Link to="/projects/new">
                                <Button>Create Project</Button>
                            </Link>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="border rounded-md">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Name</TableHead>
                                    <TableHead>Path</TableHead>
                                    <TableHead>Scans</TableHead>
                                    <TableHead>Created</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {projects.map((project: Project) => (
                                    <TableRow key={project.id}>
                                        <TableCell className="font-medium">{project.name}</TableCell>
                                        <TableCell className="text-muted-foreground">{project.path}</TableCell>
                                        <TableCell>{project.scans_count}</TableCell>
                                        <TableCell>{new Date(project.created_at).toLocaleDateString()}</TableCell>
                                        <TableCell className="text-right">
                                            <Button variant="ghost" size="sm" asChild>
                                                <Link to={`/projects/${project.id}`}>
                                                    View <ArrowRight className="ml-2 h-4 w-4" />
                                                </Link>
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                )}
            </div>
        </div>
    )
}
