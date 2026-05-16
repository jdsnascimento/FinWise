import api from './api';

export const authService = {
    async register(data) {
        const response = await api.post('/api/auth/register', data);
        return response.data;
    },

    async login(data) {
        const response = await api.post('/api/auth/login', data);
        return response.data;
    },

    async getMe() {
        const response = await api.get('/api/auth/me');
        return response.data;
    },

    async updateMe(data) {
        const response = await api.put('/api/auth/me', data);
        return response.data;
    }
};