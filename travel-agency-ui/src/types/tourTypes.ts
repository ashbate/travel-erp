// src/types/tourTypes.ts
import { UserRead } from './authTypes'; // Assuming UserRead is defined for creator

// Basic structure for TourHotelAllocation as it might appear in TourRead
export interface TourHotelAllocationClient {
  id: number;
  hotel_id: number;
  // hotel_name?: string; // Potentially denormalized data from backend
  room_configuration_id: number;
  // room_type?: string; // Potentially denormalized data from backend
  allocated_rooms: number;
  check_in_date: string; // Assuming string date e.g., "YYYY-MM-DD"
  check_out_date: string;
  created_at?: string;
  updated_at?: string;
}

export interface TourReadClient {
  id: number;
  name: string;
  description?: string | null;
  destination: string;
  start_date: string; // Assuming string date e.g., "YYYY-MM-DD"
  end_date: string;
  price_per_guest: number; // Or string if backend sends Decimal as string
  max_capacity?: number | null;
  current_bookings_count: number;
  itinerary_details?: string | null;
  created_by_user_id: number;
  creator?: UserRead | null; // Nested creator info
  hotel_allocations?: TourHotelAllocationClient[];
  created_at?: string;
  updated_at?: string;
  travel_mode?: string; // Added
}

// Enum for Travel Mode Choices (can be used in forms)
export enum TravelModeChoices {
  BUS = "Bus",
  PLANE = "Plane",
  TRAIN = "Train",
  MIXED = "Mixed",
  OTHER = "Other",
}

export interface TourCreateClient {
  name: string;
  description?: string | null;
  destination: string;
  start_date: string; // Expect YYYY-MM-DD string from date input
  end_date: string;   // Expect YYYY-MM-DD string from date input
  price_per_guest: number;
  max_capacity?: number | null;
  itinerary_details?: string | null;
  travel_mode?: string; // Added
  // created_by_user_id will be handled by backend based on authenticated user
  // or if admin, they might specify it. For now, assume backend handles it.
}

export interface TourUpdateClient {
  name?: string;
  description?: string | null;
  destination?: string;
  start_date?: string; // Expect YYYY-MM-DD string
  end_date?: string;   // Expect YYYY-MM-DD string
  price_per_guest?: number;
  max_capacity?: number | null;
  itinerary_details?: string | null;
  travel_mode?: string; // Added
  // created_by_user_id is typically not updatable directly by editor unless admin overrriding
}

// AITourPromptClient and AIGeneratedItineraryClient should already be here
export interface AITourPromptClient {
  destination: string;
  duration_days: number;
  traveler_type?: string;
  interests?: string[];
  budget_level?: string;
  preferred_activities?: string[];
}

export interface AIGeneratedItineraryClient {
  tour_name_suggestion: string;
  suggested_description: string;
  itinerary_details: string;
  estimated_price_range?: string;
  warnings?: string[];
}

export interface TourHotelAllocationUpdateClient {
  // All fields are optional for a PUT/PATCH style update
  hotel_id?: number;
  room_configuration_id?: number;
  allocated_rooms?: number;
  check_in_date?: string; // YYYY-MM-DD
  check_out_date?: string; // YYYY-MM-DD
}
