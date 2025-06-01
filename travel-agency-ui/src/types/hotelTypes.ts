// src/types/hotelTypes.ts
export interface RoomConfigurationReadClient {
  id: number;
  hotel_id: number;
  room_type: string;
  description?: string | null;
  max_occupancy: number;
  price_per_night: number; // Or string
  number_of_available_rooms: number;
  created_at?: string;
  updated_at?: string;
}

export interface HotelReadClient {
  id: number;
  name: string;
  address: string;
  city: string;
  country: string;
  star_rating?: number | null;
  contact_email?: string | null;
  contact_phone?: string | null;
  room_configurations?: RoomConfigurationReadClient[]; // Might not always be loaded with list
  created_at?: string;
  updated_at?: string;
}

// For creating an allocation (matches backend TourHotelAllocationCreate)
export interface TourHotelAllocationCreateClient {
  hotel_id: number;
  room_configuration_id: number;
  allocated_rooms: number;
  check_in_date: string; // YYYY-MM-DD
  check_out_date: string; // YYYY-MM-DD
}
