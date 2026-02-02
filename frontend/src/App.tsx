import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import NewProject from './pages/NewProject'
import ProjectDetails from './pages/ProjectDetails'
import ScanDetails from './pages/ScanDetails'

import Landing from './pages/Landing'

function App() {
    return (
        <Routes>
            <Route path="/landing" element={<Landing />} />
            <Route path="/" element={<Layout />}>
                <Route index element={<Dashboard />} />
                <Route path="projects/new" element={<NewProject />} />
                <Route path="projects/:id" element={<ProjectDetails />} />
                <Route path="scans/:id" element={<ScanDetails />} />
            </Route>
        </Routes>
    )
}

export default App
