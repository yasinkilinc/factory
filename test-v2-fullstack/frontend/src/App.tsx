import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Layout, Menu } from 'lucide-react';



import { UserPage } from './pages/UserPage';



const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r border-gray-200">
          <div className="p-6">
            <h1 className="text-xl font-bold text-gray-800">user-service</h1>
          </div>
          <nav className="mt-6">
            
            <div className="px-6 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              user
            </div>
            
            <Link 
              to="/user" 
              className="flex items-center px-6 py-3 text-gray-600 hover:bg-gray-100 transition-colors"
            >
              <Layout size={18} className="mr-3" />
              User
            </Link>
            
            
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<div className="p-8"><h2 className="text-2xl font-bold">Welcome to user-service</h2></div>} />
            
            
            <Route path="/user/*" element={<UserPage />} />
            
            
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;