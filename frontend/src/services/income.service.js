import api from './api';

export const incomeService = {
    async create(data) {
        const response = await api.post('/api/incomes/', data);
        return response.data;
    },

    async listAll(filters = {}) {
        const response = await api.get('/api/incomes/', { params: filters });
        return response.data;
    },

    async getById(id) {
        const response = await api.get(`/api/incomes/${id}`);
        return response.data;
    },

    async update(id, data) {
        const response = await api.put(`/api/incomes/${id}`, data);
        return response.data;
    },

    async receive(id) {
        const response = await api.patch(`/api/incomes/${id}/receive`);
        return response.data;
    },

    async delete(id) {
        const response = await api.delete(`/api/incomes/${id}`);
        return response.data;
    },

    async getSummary(month = null) {
        const params = month ? { month } : {};
        const response = await api.get('/api/incomes/summary', { params });
        return response.data;
    }
};