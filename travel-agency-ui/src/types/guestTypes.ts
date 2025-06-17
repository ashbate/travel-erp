// Base Guest structure
export interface GuestBase {
  first_name: string;
  last_name: string;
  email: string;
  phone_number?: string;
  date_of_birth?: string; // YYYY-MM-DD
  preferences?: string;
  // New passport fields
  passport_number?: string;
  passport_expiry_date?: string; // YYYY-MM-DD
  passport_issuing_country?: string;
  visa_details?: string;
}

// For reading guest data from the backend (includes ID and timestamps)
export interface GuestReadClient extends GuestBase {
  id: number;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

// For creating a new guest
export interface GuestCreateClient extends GuestBase {}

// For updating an existing guest (all fields optional)
export interface GuestUpdateClient {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone_number?: string;
  date_of_birth?: string;
  preferences?: string;
  passport_number?: string;
  passport_expiry_date?: string;
  passport_issuing_country?: string;
  visa_details?: string;
}
