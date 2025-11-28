import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import JobsPage from './components/JobsPage';
import JobDetail from './components/JobDetail';
import './styles/App.css';

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="logo-text">JobPortal</h1>
            <span className="logo-subtitle">Find Your Dream Job</span>
          </div>
        </div>
      </header>
      
      <main className="app-main">
        <Routes>
          <Route path="/" element={<JobsPage />} />
          <Route path="/job/:jobUrl" element={<JobDetail />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;

