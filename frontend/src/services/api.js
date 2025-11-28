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
    // Ensure page parameter is included
    const requestParams = {
      ...params,
      page: params.page || 1,
      page_size: params.page_size || 20
    };
    
    const response = await api.post('/api/jobs/search/', requestParams);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Network error. Please check if the backend is running.' };
  }
};

export const getJobDetails = async (jobUrl) => {
  try {
    const response = await api.get('/api/jobs/details/', {
      params: {
        url: jobUrl
      }
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Network error. Please check if the backend is running.' };
  }
};

export default api;

