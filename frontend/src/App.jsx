
import { useState, useEffect } from 'react'
import { Link, Routes, Route, useNavigate } from 'react-router-dom'
import { fetchAPI } from './api'
import ItemList from './components/ItemList'
import ItemForm from './components/ItemForm'
import AuthPage from './components/AuthPage'
import './global.scss'


function App() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [newItemName, setNewItemName] = useState('')
  const [newItemDesc, setNewItemDesc] = useState('')
  const [user, setUser] = useState(null)
  const navigate = useNavigate();

  useEffect(() => {
    fetchCurrentUser()
  }, [])

  const fetchCurrentUser = async () => {
    try {
      const data = await fetchAPI('/auth/me', { credentials: 'include' })
      setUser(data.user)
      if (data.user) fetchItems()
    } catch (err) {
      setUser(null)
    }
  }

  const fetchItems = async () => {
    try {
      setLoading(true)
      const data = await fetchAPI('/items', { credentials: 'include' })
      setItems(data.items || [])
      setError(null)
    } catch (err) {
      setError('Failed to fetch items: ' + err.message)
      console.error('Error fetching items:', err)
    } finally {
      setLoading(false)
    }
  }

  const createItem = async (e) => {
    e.preventDefault()
    if (!newItemName.trim()) return

    try {
      await fetchAPI('/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          name: newItemName,
          description: newItemDesc
        })
      })
      setNewItemName('')
      setNewItemDesc('')
      fetchItems()
    } catch (err) {
      setError('Failed to create item: ' + err.message)
    }
  }

  const deleteItem = async (id) => {
    try {
      await fetchAPI(`/items/${id}`, { method: 'DELETE', credentials: 'include' })
      fetchItems()
    } catch (err) {
      setError('Failed to delete item: ' + err.message)
    }
  }

  const handleAuth = (data) => {
    setUser(data.username || data.user)
    fetchItems()
  }

  const handleLogout = async () => {
    await fetchAPI('/auth/logout', { method: 'POST', credentials: 'include' })
    setUser(null)
    setItems([])
    navigate('/')
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>React + Python Boilerplate</h1>
        {user && <span style={{ marginRight: 16 }}>Logged in as <b>{user}</b></span>}
        {user ? (
          <button onClick={handleLogout}>Logout</button>
        ) : (
          <Link to="/auth" style={{ fontWeight: 'bold', color: '#007bff', marginLeft: 16 }}>Go to Auth Page</Link>
        )}
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </header>

      <main>
        <Routes>
          <Route path="/auth" element={<AuthPage onAuth={handleAuth} />} />
          <Route path="/" element={user ? (
            <>
              <ItemForm
                onSubmit={createItem}
                newItemName={newItemName}
                setNewItemName={setNewItemName}
                newItemDesc={newItemDesc}
                setNewItemDesc={setNewItemDesc}
              />
              <ItemList
                items={items}
                onDelete={deleteItem}
              />
            </>
          ) : (
            <div style={{ margin: '2em 0' }}>
              <p>Please <Link to="/auth">log in</Link> to view your todo list.</p>
            </div>
          )} />
        </Routes>
      </main>
    </div>
  )
}

export default App
