import { Link } from 'react-router-dom'
import { Shield, BookOpen, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function DocsIntro() {
    return (
        <div className="min-h-screen bg-background">
            <header className="px-6 h-16 flex items-center border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
                <Link className="flex items-center justify-center" to="/landing">
                    <Shield className="h-6 w-6 text-primary mr-2" />
                    <span className="font-bold text-lg">eidosSec</span>
                </Link>
            </header>

            <main className="container mx-auto px-4 py-12">
                <div className="max-w-3xl mx-auto space-y-6">
                    <div className="flex items-center gap-3">
                        <BookOpen className="h-8 w-8 text-primary" />
                        <h1 className="text-3xl font-bold">Documentation Intro</h1>
                    </div>

                    <p className="text-muted-foreground">
                        eidosSec menyatukan scanning multi-tool, workflow AI, dan triage findings
                        dalam satu alur terintegrasi. Untuk mulai, login dulu lalu buat project
                        dengan path container (`/app/projects/...`) agar scanner bisa mengakses repo.
                    </p>

                    <div className="rounded-lg border p-6 space-y-3">
                        <h2 className="text-xl font-semibold">Quick Start</h2>
                        <ol className="list-decimal pl-6 space-y-2 text-sm text-muted-foreground">
                            <li>Buka halaman auth dan login atau lakukan setup admin pertama.</li>
                            <li>Buat project baru dengan path yang terlihat dari container scanner.</li>
                            <li>Jalankan scan mode `quick`, monitor progress, lalu review findings.</li>
                        </ol>
                    </div>

                    <div className="flex flex-wrap gap-3">
                        <Link to="/auth">
                            <Button>Open Auth</Button>
                        </Link>
                        <Link to="/landing">
                            <Button variant="outline">
                                <ArrowLeft className="mr-2 h-4 w-4" />
                                Back to Landing
                            </Button>
                        </Link>
                    </div>
                </div>
            </main>
        </div>
    )
}
