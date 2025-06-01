import axios from 'axios';
import { LoginCredentials, TokenResponse } from '../types/authTypes';
import {
    TourReadClient, TourCreateClient, TourUpdateClient, AITourPromptClient, AIGeneratedItineraryClient,
    HotelReadClient, RoomConfigurationReadClient, TourHotelAllocationCreateClient, TourHotelAllocationClient
} from '../types'; // Ensure correct path & import TourReadClient
import { useAuthStore } from '../store/authStore'; // To get current user ID

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Add a request interceptor to include the token in headers
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken'); // Or from Zustand store
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const loginUser = async (credentials: LoginCredentials): Promise<TokenResponse> => {
  const params = new URLSearchParams();
  params.append('username', credentials.username);
  params.append('password', credentials.password);

  const response = await apiClient.post<TokenResponse>('/token/', params, {
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
  return response.data;
};

// Placeholder for fetching current user (if needed after login)
// export const fetchCurrentUser = async () => {
//   const response = await apiClient.get('/users/me');
//   return response.data;
// };

export const generateAITour = async (prompt: AITourPromptClient): Promise<AIGeneratedItineraryClient> => {
  const backendPrompt = {
    ...prompt,
    interests: prompt.interests?.length ? prompt.interests : undefined,
    preferred_activities: prompt.preferred_activities?.length ? prompt.preferred_activities : undefined,
  };
  const response = await apiClient.post<AIGeneratedItineraryClient>('/tours/generate-with-ai', backendPrompt);
  return response.data;
};

export const getAllTours = async (params?: { skip?: number; limit?: number }): Promise<TourReadClient[]> => {
  const response = await apiClient.get<TourReadClient[]>('/tours/', { params });
  return response.data;
};

export const getTourById = async (tourId: number): Promise<TourReadClient> => {
  const response = await apiClient.get<TourReadClient>(`/tours/${tourId}`);
  return response.data;
};

export const createTour = async (tourData: TourCreateClient): Promise<TourReadClient> => {
  const currentUserId = useAuthStore.getState().user?.id; // Assuming user object has id
  if (!currentUserId) {
    throw new Error('User ID not found. Cannot create tour.');
  }

  const payload = {
    ...tourData,
    created_by_user_id: currentUserId,
  };

  const response = await apiClient.post<TourReadClient>('/tours/', payload);
  return response.data;
};

export const updateTour = async (tourId: number, tourData: TourUpdateClient): Promise<TourReadClient> => {
  const response = await apiClient.put<TourReadClient>(`/tours/${tourId}`, tourData);
  return response.data;
};

export const getAllHotelsSimple = async (): Promise<Pick<HotelReadClient, 'id' | 'name'>[]> => {
  // Assuming an endpoint that returns a light list of hotels for selection
  // If not, use getAllHotels and map, or adjust backend to provide this
  const response = await apiClient.get<HotelReadClient[]>('/hotels/', { params: { limit: 1000 } }); // Fetch all for selection
  return response.data.map(h => ({ id: h.id, name: h.name }));
};

export const getRoomConfigsForHotel = async (hotelId: number): Promise<RoomConfigurationReadClient[]> => {
  const response = await apiClient.get<RoomConfigurationReadClient[]>(`/hotels/${hotelId}/room_configurations`);
  return response.data;
};

export const addHotelAllocationToTour = async (tourId: number, allocationData: TourHotelAllocationCreateClient): Promise<TourHotelAllocationClient> => {
  const response = await apiClient.post<TourHotelAllocationClient>(`/tours/${tourId}/hotel_allocations/`, allocationData);
  return response.data;
};

export const updateHotelAllocation = async (allocationId: number, allocationData: TourHotelAllocationUpdateClient): Promise<TourHotelAllocationClient> => {
  const response = await apiClient.put<TourHotelAllocationClient>(`/tours/hotel_allocations/${allocationId}`, allocationData);
  return response.data;
};

export const deleteHotelAllocation = async (allocationId: number): Promise<void> => {
  await apiClient.delete(`/tours/hotel_allocations/${allocationId}`);
  // DELETE typically returns 204 No Content, so no response body to parse.
};

// Functions for updating/deleting allocations will be added later
export default apiClient;
