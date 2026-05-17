import api from './api';

export const categoryService = {
    async listAll(type = null) {
        const params = type ? { type } : {};
        const response = await api.get('/api/categories/', { params });
        return response.data;
    }
};