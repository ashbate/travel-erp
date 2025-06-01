export interface LoginCredentials {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number; // Ensure this is present
  username: string;
  email?: string;
  full_name?: string;
  role?: string;
  // add other user fields if returned by /users/me or decoded from token
}
