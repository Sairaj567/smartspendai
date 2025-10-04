import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import '@/App.css';

// Components
import Dashboard from './components/Dashboard';
import Analytics from './components/Analytics';
import Transactions from './components/Transactions';
import AIInsights from './components/AIInsights';
import PaymentFlow from './components/PaymentFlow';
import ImportTransactions from './components/ImportTransactions';
import LandingPage from './components/LandingPage';
import AuthModal from './components/AuthModal';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showAuth, setShowAuth] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('spendsmart_user');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setCurrentUser(userData);
    setIsAuthenticated(true);
    setShowAuth(false);
    localStorage.setItem('spendsmart_user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('spendsmart_user');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="App min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <BrowserRouter>
        {!isAuthenticated ? (
          <>
            <LandingPage onGetStarted={() => setShowAuth(true)} />
            {showAuth && (
              <AuthModal
                isOpen={showAuth}
                onClose={() => setShowAuth(false)}
                onLogin={handleLogin}
              />
            )}
          </>
        ) : (
          <Routes>
            <Route
              path="/dashboard"
              element={<Dashboard user={currentUser} onLogout={handleLogout} />}
            />
            <Route
              path="/analytics"
              element={<Analytics user={currentUser} onLogout={handleLogout} />}
            />
            <Route
              path="/transactions"
              element={<Transactions user={currentUser} onLogout={handleLogout} />}
            />
            <Route
              path="/insights"
              element={<AIInsights user={currentUser} onLogout={handleLogout} />}
            />
            <Route
              path="/pay"
              element={<PaymentFlow user={currentUser} onLogout={handleLogout} />}
            />
            <Route
              path="/import"
              element={
                <ImportTransactions 
                  user={currentUser} 
                  onLogout={handleLogout}
                  onImportComplete={(result) => {
                    // Navigate to transactions page after successful import
                    window.location.href = '/transactions';
                  }}
                />
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        )}
      </BrowserRouter>
    </div>
  );
}

export default App;