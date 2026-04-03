import { useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { AlertTriangle, Loader2, Lock, Shield, UserPlus } from 'lucide-react'

import { api } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

type AuthMode = 'login' | 'setup'

export default function AuthPage() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()

    const [mode, setMode] = useState<AuthMode>('login')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState('')
    const [message, setMessage] = useState('')

    const nextPath = useMemo(() => {
        const next = searchParams.get('next')
        if (next && next.startsWith('/')) return next
        return '/'
    }, [searchParams])

    const sessionReason = searchParams.get('reason')

    const persistToken = (token: string) => {
        localStorage.setItem('token', token)
    }

    const login = async (targetEmail: string, targetPassword: string) => {
        const form = new URLSearchParams()
        form.append('username', targetEmail)
        form.append('password', targetPassword)
        const response = await api.post('/auth/login', form, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        })

        const token = response.data?.access_token
        if (!token) {
            throw new Error('Token not returned by server')
        }

        persistToken(token)
    }

    const handleLogin = async () => {
        if (!email || !password) {
            setError('Email dan password wajib diisi.')
            return
        }

        setError('')
        setMessage('')
        setIsSubmitting(true)
        try {
            await login(email, password)
            navigate(nextPath, { replace: true })
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Login gagal. Periksa kredensial Anda.')
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleSetup = async () => {
        if (!email || !password) {
            setError('Email dan password wajib diisi.')
            return
        }

        setError('')
        setMessage('')
        setIsSubmitting(true)
        try {
            await api.post('/auth/setup', { email, password })
            await login(email, password)
            setMessage('Setup admin berhasil. Anda sudah login.')
            navigate(nextPath, { replace: true })
        } catch (err: any) {
            const detail = err?.response?.data?.detail || 'Setup gagal.'
            if (typeof detail === 'string' && detail.toLowerCase().includes('setup already completed')) {
                setError('Setup sudah pernah dilakukan. Silakan login dengan akun yang sudah ada.')
                setMode('login')
            } else {
                setError(detail)
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <div className="min-h-screen bg-background flex items-center justify-center px-4 py-10">
            <Card className="w-full max-w-md">
                <CardHeader className="space-y-3">
                    <div className="flex items-center gap-2 text-primary">
                        <Shield className="h-5 w-5" />
                        <span className="font-semibold">eidosSec Authentication</span>
                    </div>
                    <CardTitle>{mode === 'login' ? 'Masuk ke eidosSec' : 'Setup Admin Pertama'}</CardTitle>
                    <CardDescription>
                        {mode === 'login'
                            ? 'Gunakan akun yang sudah terdaftar untuk mengakses dashboard.'
                            : 'Buat akun admin pertama. Endpoint ini hanya valid saat setup awal.'}
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {sessionReason === 'session_expired' && (
                        <div className="rounded-md border border-yellow-500/30 bg-yellow-500/10 px-3 py-2 text-sm text-yellow-700 flex items-start gap-2">
                            <AlertTriangle className="h-4 w-4 mt-0.5" />
                            <span>Sesi Anda berakhir atau token tidak valid. Silakan login kembali.</span>
                        </div>
                    )}

                    {error && (
                        <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                            {error}
                        </div>
                    )}

                    {message && (
                        <div className="rounded-md border border-green-500/30 bg-green-500/10 px-3 py-2 text-sm text-green-700">
                            {message}
                        </div>
                    )}

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Email</label>
                        <Input
                            type="email"
                            placeholder="you@company.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            disabled={isSubmitting}
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Password</label>
                        <Input
                            type="password"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            disabled={isSubmitting}
                        />
                    </div>
                </CardContent>
                <CardFooter className="flex flex-col gap-3">
                    <Button
                        className="w-full"
                        onClick={mode === 'login' ? handleLogin : handleSetup}
                        disabled={isSubmitting}
                    >
                        {isSubmitting ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Processing...
                            </>
                        ) : mode === 'login' ? (
                            <>
                                <Lock className="mr-2 h-4 w-4" />
                                Login
                            </>
                        ) : (
                            <>
                                <UserPlus className="mr-2 h-4 w-4" />
                                Setup Admin
                            </>
                        )}
                    </Button>

                    <Button
                        variant="ghost"
                        className="w-full"
                        onClick={() => {
                            setError('')
                            setMessage('')
                            setMode((prev) => (prev === 'login' ? 'setup' : 'login'))
                        }}
                        disabled={isSubmitting}
                    >
                        {mode === 'login'
                            ? 'Belum setup? Buat admin pertama'
                            : 'Sudah punya akun? Kembali ke login'}
                    </Button>
                </CardFooter>
            </Card>
        </div>
    )
}
