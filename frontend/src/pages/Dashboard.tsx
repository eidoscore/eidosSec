import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'

export default function Dashboard() {
    const { data: health, isLoading, isError } = useQuery({
        queryKey: ['health'],
        queryFn: () => api.get('/health'),
        refetchInterval: 30000, // Refresh every 30 seconds
    })

    return (
        <div className="space-y-8">
            {/* Welcome Section */}
            <div>
                <h1 className="text-4xl font-bold tracking-tight">Welcome to eidosSec</h1>
                <p className="text-muted-foreground mt-2">
                    AI-Powered Security Scanner with 50+ Tools
                </p>
            </div>

            {/* System Status Card */}
            <div className="border rounded-lg p-6 bg-card">
                <h2 className="text-2xl font-semibold mb-4">System Status</h2>

                <div className="space-y-3">
                    {/* Overall Status */}
                    <div className="flex items-center justify-between">
                        <span className="font-medium">Overall Status</span>
                        {isLoading ? (
                            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                        ) : isError ? (
                            <div className="flex items-center gap-2 text-destructive">
                                <XCircle className="h-5 w-5" />
                                <span>Disconnected</span>
                            </div>
                        ) : health?.data?.status === 'healthy' ? (
                            <div className="flex items-center gap-2 text-green-600">
                                <CheckCircle2 className="h-5 w-5" />
                                <span>Healthy</span>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 text-yellow-600">
                                <XCircle className="h-5 w-5" />
                                <span>Degraded</span>
                            </div>
                        )}
                    </div>

                    {/* Database Status */}
                    {!isLoading && !isError && (
                        <>
                            <div className="flex items-center justify-between">
                                <span className="font-medium">Database</span>
                                {health?.data?.database === 'connected' ? (
                                    <div className="flex items-center gap-2 text-green-600">
                                        <CheckCircle2 className="h-5 w-5" />
                                        <span>Connected</span>
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-2 text-destructive">
                                        <XCircle className="h-5 w-5" />
                                        <span>Disconnected</span>
                                    </div>
                                )}
                            </div>

                            {/* Redis Status */}
                            <div className="flex items-center justify-between">
                                <span className="font-medium">Redis</span>
                                {health?.data?.redis === 'connected' ? (
                                    <div className="flex items-center gap-2 text-green-600">
                                        <CheckCircle2 className="h-5 w-5" />
                                        <span>Connected</span>
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-2 text-destructive">
                                        <XCircle className="h-5 w-5" />
                                        <span>Disconnected</span>
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="border rounded-lg p-6 bg-card">
                    <div className="text-2xl font-bold">0</div>
                    <div className="text-sm text-muted-foreground">Projects</div>
                </div>
                <div className="border rounded-lg p-6 bg-card">
                    <div className="text-2xl font-bold">0</div>
                    <div className="text-sm text-muted-foreground">Scans Completed</div>
                </div>
                <div className="border rounded-lg p-6 bg-card">
                    <div className="text-2xl font-bold">0</div>
                    <div className="text-sm text-muted-foreground">Total Findings</div>
                </div>
            </div>

            {/* Getting Started */}
            <div className="border rounded-lg p-6 bg-card">
                <h2 className="text-2xl font-semibold mb-4">Getting Started</h2>
                <div className="space-y-3 text-sm">
                    <div className="flex items-start gap-3">
                        <div className="rounded-full bg-primary/10 text-primary font-semibold h-6 w-6 flex items-center justify-center flex-shrink-0">
                            1
                        </div>
                        <div>
                            <div className="font-medium">Create a Project</div>
                            <div className="text-muted-foreground">
                                Add your first codebase to start scanning for vulnerabilities
                            </div>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <div className="rounded-full bg-primary/10 text-primary font-semibold h-6 w-6 flex items-center justify-center flex-shrink-0">
                            2
                        </div>
                        <div>
                            <div className="font-medium">Run a Quick Scan</div>
                            <div className="text-muted-foreground">
                                Start with a Quick Scan (15 tools, ~10 minutes)
                            </div>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <div className="rounded-full bg-primary/10 text-primary font-semibold h-6 w-6 flex items-center justify-center flex-shrink-0">
                            3
                        </div>
                        <div>
                            <div className="font-medium">Review Findings</div>
                            <div className="text-muted-foreground">
                                Analyze security issues by severity, type, and file location
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
