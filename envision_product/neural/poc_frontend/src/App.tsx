import React from 'react';
import { Provider } from 'react-redux';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { store } from './store';
import './App.css';

// Import pages
// import UploadPage from './pages/UploadPage';
import ResultsPage from './pages/ResultsPage';
import DashboardPage from './pages/DashboardPage';
// ... other imports

function App() {
  return (
    <Provider store={store}>
      <Router>
        <div className="App">
          <Routes>
            {/* Define routes here */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/results/:modelId" element={<ResultsPage />} />
            <Route path="/results" element={<ResultsPage />} />
            {/* ... other routes */}
          </Routes>
        </div>
      </Router>
    </Provider>
  );
}

export default App;
