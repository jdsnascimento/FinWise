import api from './api';

export const categoryService = {
    async listAll(type = null) {
        const params = type ? { type } : {};
        const response = await api.get('/api/categories/', { params });
        return response.data;
    },

    async create(data) {
        const response = await api.post('/api/categories/', data);
        return response.data;
    },

    async update(id, data) {
        const { name, icon, color } = data;
        const response = await api.put(`/api/categories/${id}`, { name, icon, color });
        return response.data;
    },

    async delete(id) {
        const response = await api.delete(`/api/categories/${id}`);
        return response.data;
    }
};
