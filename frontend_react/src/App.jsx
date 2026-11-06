import React, { useState } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import SignInModal from './components/SignInModal';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('landing'); // 'landing' | 'dashboard'
  const [isSignInOpen, setIsSignInOpen] = useState(false);
  const [user, setUser] = useState(null);

  const handleLaunchWorkstation = () => {
    setActiveTab('dashboard');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleOpenSignIn = () => {
    setIsSignInOpen(true);
  };

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setIsSignInOpen(false);
    setActiveTab('dashboard');
  };

  const handleSignOut = () => {
    setUser(null);
    setActiveTab('landing');
  };

  return (
    <div className="sixth-design" style={{ minHeight: '100vh', position: 'relative', background: 'var(--bg)' }}>
      {/* Glassmorphism Header Bar */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={(tab) => {
          if (tab === 'login') {
            setIsSignInOpen(true);
          } else {
            setActiveTab(tab);
          }
        }} 
        user={user}
        onSignOut={handleSignOut}
      />

      {/* Main View Router */}
      <main>
        {activeTab === 'landing' ? (
          <LandingPage 
            onLaunchWorkstation={handleLaunchWorkstation}
            onOpenSignIn={handleOpenSignIn}
          />
        ) : (
          <Dashboard />
        )}
      </main>

      {/* Glassmorphism Sign-In Modal */}
      <SignInModal 
        isOpen={isSignInOpen}
        onClose={() => setIsSignInOpen(false)}
        onLoginSuccess={handleLoginSuccess}
      />

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--line)', padding: '24px 28px', textTransform: 'uppercase', letterSpacing: '0.12em', fontSize: '11px', color: 'var(--text-3)', textAlign: 'center' }}>
        CARE-XAI Multimodal Diagnostic Engine · CMMD Mammography Benchmark · FastAPI + PyTorch Backend
      </footer>
    </div>
  );
}
