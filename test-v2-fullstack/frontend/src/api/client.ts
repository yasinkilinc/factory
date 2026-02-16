import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});


// Module: user

export const UserApi = {
  getAll: async () => {
    const response = await api.get('/user/user');
    return response.data;
  },
  getOne: async (id: string) => {
    const response = await api.get(`/user/user/${id}`);
    return response.data;
  },
  create: async (data: any) => {
    const response = await api.post('/user/user', data);
    return response.data;
  },
  update: async (id: string, data: any) => {
    const response = await api.put(`/user/user/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    await api.delete(`/user/user/${id}`);
  },
};

