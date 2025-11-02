/**
 * Main App Component with Routing
 */
import { Routes, Route, Navigate } from 'react-router-dom';
import StarlinkTracker from './components/StarlinkTracker';

function App() {
  return (
    <Routes>
      <Route path="/" element={<StarlinkTracker />} />
      <Route path="/tracker" element={<StarlinkTracker />} />
      {/* Redirect any old routes to tracker */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
