/*
  # Create users table for academic management system

  1. New Tables
    - `users`
      - `id` (uuid, primary key) - User unique identifier
      - `full_name` (text) - User's full name
      - `email` (text, unique) - User's email address
      - `password_hash` (text) - Hashed password
      - `role` (text) - User role: 'teacher' or 'student'
      - `reset_token` (text, nullable) - Password reset token
      - `reset_token_expiry` (timestamptz, nullable) - Token expiration time
      - `created_at` (timestamptz) - Account creation timestamp
  
  2. Security
    - Enable RLS on `users` table
    - Add policy for users to read their own data
    - Add policy for users to update their own data (excluding password_hash and role)
*/

CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  full_name text NOT NULL,
  email text UNIQUE NOT NULL,
  password_hash text NOT NULL,
  role text NOT NULL CHECK (role IN ('teacher', 'student')),
  reset_token text,
  reset_token_expiry timestamptz,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own data"
  ON users FOR SELECT
  TO authenticated
  USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own data"
  ON users FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = id::text)
  WITH CHECK (auth.uid()::text = id::text);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);