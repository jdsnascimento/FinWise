import api from './api';

export const creditCardService = {
    async listAll(activeOnly = false) {
        const response = await api.get('/api/credit-cards/', {
            params: { active_only: activeOnly }
        });
        return response.data;
    },

    async getSummary() {
        const response = await api.get('/api/credit-cards/summary');
        return response.data;
    },

    async getById(id) {
        const response = await api.get(`/api/credit-cards/${id}`);
        return response.data;
    },

    async getDetails(id) {
        const response = await api.get(`/api/credit-cards/${id}/details`);
        return response.data;
    },

    async create(data) {
        const response = await api.post('/api/credit-cards/', data);
        return response.data;
    },

    async update(id, data) {
        const response = await api.put(`/api/credit-cards/${id}`, data);
        return response.data;
    },

    async delete(id) {
        const response = await api.delete(`/api/credit-cards/${id}`);
        return response.data;
    }
};