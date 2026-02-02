import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2, FolderOpen, Code2, CheckCircle2, AlertTriangle, ArrowRight, ArrowLeft } from 'lucide-react'
import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

export default function NewProject() {
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const [step, setStep] = useState(1)
    const [formData, setFormData] = useState({
        name: '',
        path: '',
        framework: 'auto',
    })
    const [error, setError] = useState('')

    // Mock detection loading state
    const [isDetecting, setIsDetecting] = useState(false)
    const [detectedInfo, setDetectedInfo] = useState<{ languages: string[], framework: string } | null>(null)

    const createProjectMutation = useMutation({
        mutationFn: (data: any) => api.post('/projects', data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] })
            navigate('/')
        },
        onError: (error: any) => {
            setError(error.response?.data?.detail || 'Failed to create project')
        }
    })

    const handlePathSubmit = async () => {
        if (!formData.name || !formData.path) {
            setError('Please fill in all fields')
            return
        }

        setError('')
        setIsDetecting(true)

        // Simulate detection delay (in real app, assume backend does this or we call a detect endpoint)
        // For now, we'll just check if the path looks real or just move to next step
        setTimeout(() => {
            setIsDetecting(false)
            // Mock result
            setDetectedInfo({
                languages: ['Python', 'JavaScript'],
                framework: 'FastAPI'
            })
            setStep(2)
        }, 1500)
    }

    const handleCreate = () => {
        createProjectMutation.mutate({
            name: formData.name,
            path: formData.path,
            languages: detectedInfo?.languages || [],
            framework: detectedInfo?.framework || 'Unknown',
            settings: {}
        })
    }

    return (
        <div className="max-w-2xl mx-auto py-8">
            <h1 className="text-3xl font-bold mb-8">New Project</h1>

            <div className="flex items-center gap-4 mb-8">
                <div className={`rounded-full h-8 w-8 flex items-center justify-center text-sm font-medium ${step >= 1 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}>1</div>
                <div className="h-1 bg-muted flex-1" />
                <div className={`rounded-full h-8 w-8 flex items-center justify-center text-sm font-medium ${step >= 2 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}>2</div>
                <div className="h-1 bg-muted flex-1" />
                <div className={`rounded-full h-8 w-8 flex items-center justify-center text-sm font-medium ${step >= 3 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}>3</div>
            </div>

            {step === 1 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Project Details</CardTitle>
                        <CardDescription>Enter the path to the local source code you want to scan.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Project Name</label>
                            <Input
                                placeholder="e.g. My Backend API"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Local Path</label>
                            <div className="flex gap-2">
                                <Input
                                    placeholder="e.g. /home/user/projects/my-app"
                                    value={formData.path}
                                    onChange={(e) => setFormData({ ...formData, path: e.target.value })}
                                />
                            </div>
                            <p className="text-xs text-muted-foreground">Absolute path to the project root directory.</p>
                        </div>

                        {error && (
                            <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md flex items-center gap-2">
                                <AlertTriangle className="h-4 w-4" />
                                {error}
                            </div>
                        )}
                    </CardContent>
                    <CardFooter className="flex justify-end">
                        <Button onClick={handlePathSubmit} disabled={isDetecting}>
                            {isDetecting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Analyzing...
                                </>
                            ) : (
                                <>
                                    Next <ArrowRight className="ml-2 h-4 w-4" />
                                </>
                            )}
                        </Button>
                    </CardFooter>
                </Card>
            )}

            {step === 2 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Review configuration</CardTitle>
                        <CardDescription>We've detected the following details about your project.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="flex items-start gap-4 p-4 border rounded-lg bg-muted/50">
                            <FolderOpen className="h-5 w-5 mt-0.5 text-muted-foreground" />
                            <div>
                                <div className="font-medium">Project Source</div>
                                <div className="text-sm text-muted-foreground">{formData.path}</div>
                            </div>
                        </div>

                        <div className="flex items-start gap-4 p-4 border rounded-lg bg-muted/50">
                            <Code2 className="h-5 w-5 mt-0.5 text-muted-foreground" />
                            <div className="space-y-2">
                                <div className="font-medium">Technology Stack</div>
                                <div className="flex flex-wrap gap-2">
                                    {detectedInfo?.languages.map(lang => (
                                        <Badge key={lang} variant="secondary">{lang}</Badge>
                                    ))}
                                    <Badge variant="outline">{detectedInfo?.framework}</Badge>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button variant="ghost" onClick={() => setStep(1)}>
                            <ArrowLeft className="mr-2 h-4 w-4" /> Back
                        </Button>
                        <Button onClick={() => setStep(3)}>
                            Looks Good <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </CardFooter>
                </Card>
            )}

            {step === 3 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Ready to Scan?</CardTitle>
                        <CardDescription>Create the project and start your first security scan.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="bg-green-500/10 text-green-600 p-4 rounded-lg flex items-center gap-3">
                            <CheckCircle2 className="h-5 w-5" />
                            <div>
                                <div className="font-medium">Configuration Validated</div>
                                <div className="text-sm">Your project is ready to be onboarded.</div>
                            </div>
                        </div>
                        <p className="text-sm text-muted-foreground">
                            This will create the project entry in the database. You can start a scan immediately after.
                        </p>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button variant="ghost" onClick={() => setStep(2)}>
                            <ArrowLeft className="mr-2 h-4 w-4" /> Back
                        </Button>
                        <Button onClick={handleCreate} disabled={createProjectMutation.isPending}>
                            {createProjectMutation.isPending ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating...
                                </>
                            ) : (
                                'Create Project'
                            )}
                        </Button>
                    </CardFooter>
                </Card>
            )}
        </div>
    )
}
