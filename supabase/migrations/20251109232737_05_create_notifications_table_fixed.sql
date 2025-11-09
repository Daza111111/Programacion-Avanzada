/*
  # Create notifications table for academic management system

  1. New Tables
    - `notifications`
      - `id` (uuid, primary key) - Notification unique identifier
      - `user_id` (uuid) - Foreign key to users table
      - `message` (text) - Notification message
      - `type` (text) - Notification type
      - `read` (boolean) - Read status
      - `created_at` (timestamptz) - Notification creation timestamp
  
  2. Security
    - Enable RLS on `notifications` table
    - Add policies for users
*/

CREATE TABLE IF NOT EXISTS notifications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  message text NOT NULL,
  type text NOT NULL,
  read boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone authenticated can read notifications"
  ON notifications FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Anyone authenticated can update notifications"
  ON notifications FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Anyone authenticated can create notifications"
  ON notifications FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);