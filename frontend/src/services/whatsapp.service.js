import api from './api';

export const whatsappService = {
    async createInstance(data) {
        const response = await api.post('/api/whatsapp/instance/create', data);
        return response.data;
    },

    async getQrCode() {
        const response = await api.get('/api/whatsapp/instance/qrcode');
        return response.data;
    },

    async getStatus() {
        const response = await api.get('/api/whatsapp/instance/status');
        return response.data;
    },

    async testParse(message) {
        const response = await api.post('/api/whatsapp/test-message', { message });
        return response.data;
    }
};