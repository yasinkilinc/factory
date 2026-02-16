import React, { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { UserList } from '../components/User/UserList';
import { UserForm } from '../components/User/UserForm';
import { Plus } from 'lucide-react';

export const UserPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">User Management</h2>
        <button 
          onClick={() => navigate('new')}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <Plus size={18} className="mr-2" />
          Add User
        </button>
      </div>

      <Routes>
        <Route index element={<UserList />} />
        <Route path="new" element={<UserForm />} />
        <Route path="edit/:id" element={<UserForm />} />
      </Routes>
    </div>
  );
};