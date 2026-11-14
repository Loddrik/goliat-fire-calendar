import { StrictMode, Suspense, lazy } from 'react'
import { createRoot } from 'react-dom/client'

// "/" es la landing y "/explorar" la app. Cada una se carga aparte, así la landing no baja MapLibre.
const App = lazy(() => import('./App.tsx'))
const Landing = lazy(() => import('./landing/Landing.tsx'))

const path = location.pathname.replace(/\/+$/, '') || '/'
const params = new URLSearchParams(location.search)
// Enlaces antiguos (impresiones, WhatsApp): "/?cut=…" sigue abriendo la comuna, con todos sus parámetros.
if (path === '/' && (params.has('cut') || params.has('view'))) {
  history.replaceState(null, '', `/explorar${location.search}${location.hash}`)
}
const page = location.pathname.replace(/\/+$/, '') === '/explorar' ? <App /> : <Landing />

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Suspense fallback={null}>{page}</Suspense>
  </StrictMode>,
)
