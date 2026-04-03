import { Navigate, Outlet, Route, Routes, useLocation } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import NewProject from './pages/NewProject'
import ProjectDetails from './pages/ProjectDetails'
import ScanDetails from './pages/ScanDetails'
import Landing from './pages/Landing'
import AuthPage from './pages/Auth'
import DocsIntro from './pages/DocsIntro'

function hasToken(): boolean {
    return Boolean(localStorage.getItem('token'))
}

function RequireAuth() {
    const location = useLocation()
    if (!hasToken()) {
        const next = `${location.pathname}${location.search}`
        return <Navigate to={`/auth?next=${encodeURIComponent(next)}`} replace />
    }
    return <Outlet />
}

function RedirectIfAuthenticated() {
    if (hasToken()) {
        return <Navigate to="/" replace />
    }
    return <AuthPage />
}

function App() {
    return (
        <Routes>
            <Route path="/auth" element={<RedirectIfAuthenticated />} />
            <Route path="/landing" element={<Landing />} />
            <Route path="/docs/intro" element={<DocsIntro />} />
            <Route element={<RequireAuth />}>
                <Route path="/" element={<Layout />}>
                    <Route index element={<Dashboard />} />
                    <Route path="projects/new" element={<NewProject />} />
                    <Route path="projects/:id" element={<ProjectDetails />} />
                    <Route path="scans/:id" element={<ScanDetails />} />
                </Route>
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    )
}

export default App
