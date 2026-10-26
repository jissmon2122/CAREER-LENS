import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { JobProvider } from './context/JobContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';

import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ResumeUpload from './pages/ResumeUpload';
import SkillGapPage from './pages/SkillGapPage';
import LearningRoadmapPage from './pages/LearningRoadmapPage';
import SkillDemandPage from './pages/SkillDemandPage';
import LiveJobSearchPage from './pages/LiveJobSearchPage';
import SalaryPredictionPage from './pages/SalaryPredictionPage';

function App() {
  return (
    <AuthProvider>
      <JobProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <div className="app-container">
            <Navbar />
            <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/jobs/search"
                element={
                  <ProtectedRoute>
                    <LiveJobSearchPage />
                  </ProtectedRoute>
                }
              />
              
              <Route
                path="/resume-upload"
                element={
                  <ProtectedRoute>
                    <ResumeUpload />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/dashboard/skill-gap/:jobId"
                element={
                  <ProtectedRoute>
                    <SkillGapPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/dashboard/roadmap/:jobId"
                element={
                  <ProtectedRoute>
                    <LearningRoadmapPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/dashboard/skill-demand"
                element={
                  <ProtectedRoute>
                    <SkillDemandPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/salary"
                element={
                  <SalaryPredictionPage />
                }
              />

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
      </JobProvider>
    </AuthProvider>
  );
}

export default App;
