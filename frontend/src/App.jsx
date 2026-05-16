import { useEffect, useState } from 'react'
import api from './services/api'
import './App.css'

function App() {
  const [message, setMessage] = useState('')

  useEffect(() => {
    api.get('/')
      .then(res => setMessage(res.data.message))
      .catch(err => console.error(err))
  }, [])

  return (
    <div>
      <h1>FinWise</h1>
      <p>Backend: {message || 'Conectando...'}</p>
    </div>
  )
}

export default App