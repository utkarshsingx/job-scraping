import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchJobs = async (params) => {
  try {
    const response = await api.post('/api/jobs/search/', params);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Network error. Please check if the backend is running.' };
  }
};

export default api;

