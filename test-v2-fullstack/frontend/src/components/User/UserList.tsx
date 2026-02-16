import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserApi } from '../../api/client';
import { Edit2, Trash2 } from 'lucide-react';

export const UserList: React.FC = () => {
  const [items, setItems] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      const data = await UserApi.getAll();
      setItems(data);
    } catch (error) {
      console.error('Failed to load items', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      try {
        await UserApi.delete(id);
        loadItems();
      } catch (error) {
        console.error('Failed to delete item', error);
      }
    }
  };

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              id
            </th>
            
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              email
            </th>
            
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              name
            </th>
            
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              age
            </th>
            
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              created_at
            </th>
            
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {items.map((item) => (
            <tr key={item.id}>
              
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {String(item.id)}
              </td>
              
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {String(item.email)}
              </td>
              
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {String(item.name)}
              </td>
              
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {String(item.age)}
              </td>
              
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {String(item.created_at)}
              </td>
              
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button 
                  onClick={() => navigate(`edit/${item.id}`)}
                  className="text-blue-600 hover:text-blue-900 mr-4"
                >
                  <Edit2 size={16} />
                </button>
                <button 
                  onClick={() => handleDelete(item.id)}
                  className="text-red-600 hover:text-red-900"
                >
                  <Trash2 size={16} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};