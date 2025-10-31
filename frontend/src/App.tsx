/**
 * Main App Component with Routing
 */
import { Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import StarlinkTracker from './components/StarlinkTracker';
import ContactPage from './components/ContactPage';
import ComingSoon from './components/ComingSoon';

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/tracker" element={<StarlinkTracker />} />
      <Route path="/contact" element={<ContactPage />} />
      <Route path="/project-alpha" element={<ComingSoon projectName="Project Alpha" />} />
      <Route path="/project-beta" element={<ComingSoon projectName="Project Beta" />} />
    </Routes>
  );
}

export default App;
