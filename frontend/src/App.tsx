import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LiveChatPage from './pages/LiveChatPage'
import HistoryPage from './pages/HistoryPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="live-chat" element={<LiveChatPage />} />
        <Route path="history" element={<HistoryPage />} />
      </Route>
    </Routes>
  )
}

export default App 