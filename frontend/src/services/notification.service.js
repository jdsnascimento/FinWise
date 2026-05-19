import api from './api';

export const notificationService = {
    async getUpcomingBills() {
        const response = await api.get('/api/notifications/upcoming-bills');
        return response.data;
    },

    async getCardAlerts() {
        const response = await api.get('/api/notifications/card-alerts');
        return response.data;
    },

    async getAllNotifications() {
        const [bills, alerts] = await Promise.all([
            this.getUpcomingBills(),
            this.getCardAlerts()
        ]);
        return { bills, alerts };
    }
};