import { useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'
import Landing from './pages/Landing'
import AppPage from './pages/AppPage'
import StorePage from './pages/StorePage'

export default function App() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/app" element={<AppPage />} />
      <Route path="/tienda" element={<StorePage />} />
      <Route path="*" element={<Landing />} />
    </Routes>
  )
}
