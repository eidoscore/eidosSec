import { Link } from 'react-router-dom'
import { Shield, Zap, ArrowRight, Code, Brain } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Landing() {
    return (
        <div className="flex flex-col min-h-screen">
            {/* Header */}
            <header className="px-6 h-16 flex items-center border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
                <Link className="flex items-center justify-center" to="/">
                    <Shield className="h-6 w-6 text-primary mr-2" />
                    <span className="font-bold text-lg">eidosSec</span>
                </Link>
                <nav className="ml-auto flex gap-4 sm:gap-6">
                    <Link className="text-sm font-medium hover:underline underline-offset-4" to="/docs/intro">
                        Documentation
                    </Link>
                    <Link className="text-sm font-medium hover:underline underline-offset-4" to="https://github.com/your-org/eidosSec">
                        GitHub
                    </Link>
                </nav>
            </header>

            {/* Hero Section */}
            <main className="flex-1">
                <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-gradient-to-b from-background to-muted/50">
                    <div className="container px-4 md:px-6">
                        <div className="flex flex-col items-center space-y-4 text-center">
                            <div className="space-y-2">
                                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                                    Secure your code at the <span className="text-primary">speed of thought</span>
                                </h1>
                                <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
                                    AI-powered security scanning that understands your context. Find vulnerabilities, get fix suggestions, and verify with confidence.
                                </p>
                            </div>
                            <div className="space-x-4">
                                <Link to="/">
                                    <Button size="lg" className="h-11 px-8">
                                        Get Started <ArrowRight className="ml-2 h-4 w-4" />
                                    </Button>
                                </Link>
                                <Link to="https://github.com">
                                    <Button variant="outline" size="lg" className="h-11 px-8">
                                        View Code
                                    </Button>
                                </Link>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Features Section */}
                <section className="w-full py-12 md:py-24 lg:py-32 bg-background">
                    <div className="container px-4 md:px-6">
                        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-3">
                            <div className="flex flex-col items-center text-center space-y-3 p-6 border rounded-lg shadow-sm">
                                <Zap className="h-12 w-12 text-yellow-500 mb-2" />
                                <h3 className="text-xl font-bold">Lightning Fast</h3>
                                <p className="text-muted-foreground">
                                    Parallel execution of multiple security tools ensures you get results in minutes, not hours.
                                </p>
                            </div>
                            <div className="flex flex-col items-center text-center space-y-3 p-6 border rounded-lg shadow-sm">
                                <Brain className="h-12 w-12 text-purple-500 mb-2" />
                                <h3 className="text-xl font-bold">AI Verification</h3>
                                <p className="text-muted-foreground">
                                    Large Language Models analyze findings to filter false positives and explain complex vulnerabilities.
                                </p>
                            </div>
                            <div className="flex flex-col items-center text-center space-y-3 p-6 border rounded-lg shadow-sm">
                                <Code className="h-12 w-12 text-blue-500 mb-2" />
                                <h3 className="text-xl font-bold">Multi-Language</h3>
                                <p className="text-muted-foreground">
                                    Support for Python, JavaScript, Go, Java, and more out of the box with auto-detection.
                                </p>
                            </div>
                        </div>
                    </div>
                </section>

                {/* CTA Section */}
                <section className="w-full py-12 md:py-24 lg:py-32 bg-muted/50 border-t">
                    <div className="container px-4 md:px-6">
                        <div className="flex flex-col items-center justify-center space-y-4 text-center">
                            <div className="space-y-2">
                                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Ready to secure your project?</h2>
                                <p className="mx-auto max-w-[600px] text-muted-foreground md:text-xl">
                                    Join thousands of developers using eidosSec to ship secure code.
                                </p>
                            </div>
                            <div className="w-full max-w-sm space-y-2">
                                <Link to="/">
                                    <Button className="w-full" size="lg">Start Scanning Now</Button>
                                </Link>
                            </div>
                        </div>
                    </div>
                </section>
            </main>

            <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t">
                <p className="text-xs text-muted-foreground">© 2024 eidosSec. All rights reserved.</p>
                <nav className="sm:ml-auto flex gap-4 sm:gap-6">
                    <Link className="text-xs hover:underline underline-offset-4 text-muted-foreground" to="#">
                        Terms of Service
                    </Link>
                    <Link className="text-xs hover:underline underline-offset-4 text-muted-foreground" to="#">
                        Privacy
                    </Link>
                </nav>
            </footer>
        </div>
    )
}
