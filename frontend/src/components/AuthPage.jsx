
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchAPI } from '../api';

export default function AuthPage({ onAuth }) {
    const [mode, setMode] = useState('login');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        const endpoint = mode === 'register' ? '/auth/register' : '/auth/login';
        try {
            const data = await fetchAPI(endpoint, {
                method: 'POST',
                credentials: 'include',
                body: JSON.stringify({ username, password }),
            });
            if (data.error) throw new Error(data.error || 'Unknown error');
            onAuth && onAuth(data);
            navigate('/');
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="auth-page">
            <h2>{mode === 'register' ? 'Register' : 'Login'}</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    required
                />
                <button type="submit">{mode === 'register' ? 'Register' : 'Login'}</button>
            </form>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <p>
                {mode === 'login' ? (
                    <>Don't have an account?{' '}
                        <button onClick={() => setMode('register')}>Register</button>
                    </>
                ) : (
                    <>Already have an account?{' '}
                        <button onClick={() => setMode('login')}>Login</button>
                    </>
                )}
            </p>
        </div>
    );
}
