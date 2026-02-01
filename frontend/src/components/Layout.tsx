import { Outlet, Link } from 'react-router-dom'
import { Shield, Menu } from 'lucide-react'

export default function Layout() {
    return (
        <div className="min-h-screen bg-background">
            {/* Header */}
            <header className="border-b">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Shield className="h-6 w-6 text-primary" />
                        <Link to="/" className="text-xl font-bold">
                            eidosSec
                        </Link>
                    </div>

                    <nav className="hidden md:flex gap-6">
                        <Link
                            to="/"
                            className="text-sm font-medium hover:text-primary transition-colors"
                        >
                            Dashboard
                        </Link>
                        <Link
                            to="/projects"
                            className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
                        >
                            Projects
                        </Link>
                        <Link
                            to="/scans"
                            className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
                        >
                            Scans
                        </Link>
                    </nav>

                    <button className="md:hidden">
                        <Menu className="h-6 w-6" />
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-8">
                <Outlet />
            </main>

            {/* Footer */}
            <footer className="border-t mt-auto">
                <div className="container mx-auto px-4 py-6 text-center text-sm text-muted-foreground">
                    <p>© 2026 eidosSec. Built with ❤️ for secure code.</p>
                </div>
            </footer>
        </div>
    )
}
