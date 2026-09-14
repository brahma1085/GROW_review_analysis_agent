import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Admin } from './pages/Admin';
import { Pulse } from './pages/Pulse';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="admin" element={<Admin />} />
          <Route path="trends" element={<Pulse />} />
          <Route path="product-areas" element={<div className="p-8 text-center text-slate-500">Product Areas module coming soon.</div>} />
          <Route path="voc" element={<div className="p-8 text-center text-slate-500">VoC Explorer module coming soon.</div>} />
          <Route path="logs" element={<div className="p-8 text-center text-slate-500">Logs & History module coming soon.</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
