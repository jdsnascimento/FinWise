import api from './api';

export const dashboardService = {
    async getSummary(billingMonth = null) {
        const params = billingMonth ? { billing_month: billingMonth } : {};
        const response = await api.get('/api/dashboard/summary', { params });
        return response.data;
    }
};