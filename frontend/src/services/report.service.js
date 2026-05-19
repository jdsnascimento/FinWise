import api from './api';

export const reportService = {
    async byCategory(startDate, endDate) {
        const response = await api.get('/api/reports/by-category', {
            params: { start_date: startDate, end_date: endDate }
        });
        return response.data;
    },

    async byCard(startDate, endDate) {
        const response = await api.get('/api/reports/by-card', {
            params: { start_date: startDate, end_date: endDate }
        });
        return response.data;
    },

    async monthlyEvolution(months = 12) {
        const response = await api.get('/api/reports/monthly-evolution', {
            params: { months }
        });
        return response.data;
    },

    async paymentMethods(startDate, endDate) {
        const response = await api.get('/api/reports/payment-methods', {
            params: { start_date: startDate, end_date: endDate }
        });
        return response.data;
    },

    async fullReport(startDate, endDate) {
        const response = await api.get('/api/reports/full-report', {
            params: { start_date: startDate, end_date: endDate }
        });
        return response.data;
    }
};