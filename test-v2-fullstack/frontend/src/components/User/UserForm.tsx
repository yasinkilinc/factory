import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { UserApi } from '../../api/client';

export const UserForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [formData, setFormData] = useState<any>({});

  useEffect(() => {
    if (id) {
      loadItem();
    }
  }, [id]);

  const loadItem = async () => {
    try {
      const data = await UserApi.getOne(id!);
      setFormData(data);
    } catch (error) {
      console.error('Failed to load item', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (id) {
        await UserApi.update(id, formData);
      } else {
        await UserApi.create(formData);
      }
      navigate('/user');
    } catch (error) {
      console.error('Failed to save item', error);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6 max-w-2xl">
      <h3 className="text-lg font-medium text-gray-900 mb-6">
        {id ? 'Edit' : 'Create'} User
      </h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        
        
        
        
        <div>
          <label className="block text-sm font-medium text-gray-700">email</label>
          <input
            type="text"
            value={formData.email || ''}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
        
        
        
        <div>
          <label className="block text-sm font-medium text-gray-700">name</label>
          <input
            type="text"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
        
        
        
        <div>
          <label className="block text-sm font-medium text-gray-700">age</label>
          <input
            type="number"
            value={formData.age || ''}
            onChange={(e) => setFormData({ ...formData, age: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
        
        
        
        <div>
          <label className="block text-sm font-medium text-gray-700">created_at</label>
          <input
            type="text"
            value={formData.created_at || ''}
            onChange={(e) => setFormData({ ...formData, created_at: e.target.value })}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
        
        
        <div className="flex justify-end space-x-3 mt-6">
          <button
            type="button"
            onClick={() => navigate('/user')}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Save
          </button>
        </div>
      </form>
    </div>
  );
};