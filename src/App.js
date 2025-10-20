import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Components
import Navbar from './components/Navbar';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import BusinessPlanGenerator from './components/BusinessPlanGenerator';
import ProposalUpload from './components/ProposalUpload';
import ProposalAnalysis from './components/ProposalAnalysis';
import FundingRecommendations from './components/FundingRecommendations';
import { AuthProvider, useAuth } from './contexts/AuthContext';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function ProtectedRoute({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <div className="App">
            <Navbar />
            <Routes>
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
                path="/generate-plan" 
                element={
                  <ProtectedRoute>
                    <BusinessPlanGenerator />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/upload-proposal" 
                element={
                  <ProtectedRoute>
                    <ProposalUpload />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/analyze/:id" 
                element={
                  <ProtectedRoute>
                    <ProposalAnalysis />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/funding/:id" 
                element={
                  <ProtectedRoute>
                    <FundingRecommendations />
                  </ProtectedRoute>
                } 
              />
              <Route path="/" element={<Navigate to="/dashboard" />} />
            </Routes>
            <ToastContainer
              position="top-right"
              autoClose={5000}
              hideProgressBar={false}
              newestOnTop={false}
              closeOnClick
              rtl={false}
              pauseOnFocusLoss
              draggable
              pauseOnHover
            />
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
