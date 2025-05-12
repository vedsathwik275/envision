import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ApiResponse, ApiError } from '../types/api.types';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add authorization header if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    const apiError: ApiError = {
      status: error.response?.status || 500,
      message: 'An unexpected error occurred',
      details: error.response?.data || error.message,
    };

    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      const responseData = error.response.data as any;
      apiError.message = responseData?.message || 'Server error';
    } else if (error.request) {
      // The request was made but no response was received
      apiError.message = 'No response from server';
    }

    return Promise.reject(apiError);
  }
);

// Generic request function
export const request = async <T>(config: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  try {
    const response = await api(config);
    return {
      data: response.data,
      status: response.status,
    };
  } catch (error) {
    throw error;
  }
};

export default api; 