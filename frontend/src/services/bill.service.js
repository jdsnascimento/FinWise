import api from './api';

export const billService = {
    async create(data) {
        const response = await api.post('/api/bills/', data);
        return response.data;
    },

    async listAll(filters = {}) {
        const response = await api.get('/api/bills/', { params: filters });
        return response.data;
    },

    async getById(id) {
        const response = await api.get(`/api/bills/${id}`);
        return response.data;
    },

    async update(id, data) {
        const response = await api.put(`/api/bills/${id}`, data);
        return response.data;
    },

    async pay(id) {
        const response = await api.patch(`/api/bills/${id}/pay`);
        return response.data;
    },

    async cancel(id) {
        const response = await api.patch(`/api/bills/${id}/cancel`);
        return response.data;
    },

    async delete(id) {
        const response = await api.delete(`/api/bills/${id}`);
        return response.data;
    },

    async getSummary(billingMonth = null) {
        const params = billingMonth ? { billing_month: billingMonth } : {};
        const response = await api.get('/api/bills/summary', { params });
        return response.data;
    }
};