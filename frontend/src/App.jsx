import { useState, useEffect } from 'react'
import { fetchAPI } from './api'
import ItemList from './components/ItemList'
import ItemForm from './components/ItemForm'
import './global.scss'

function App() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [newItemName, setNewItemName] = useState('')
  const [newItemDesc, setNewItemDesc] = useState('')

  useEffect(() => {
    fetchItems()
  }, [])

  const fetchItems = async () => {
    try {
      setLoading(true)
      const data = await fetchAPI('/items')
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
      await fetchAPI(`/items/${id}`, { method: 'DELETE' })
      fetchItems()
    } catch (err) {
      setError('Failed to delete item: ' + err.message)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>React + Python Boilerplate</h1>
        {loading && <p>Loading...</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </header>

      <main>
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
      </main>
    </div>
  )
}

export default App
