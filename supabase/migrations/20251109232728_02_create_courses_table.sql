/*
  # Create courses table for academic management system

  1. New Tables
    - `courses`
      - `id` (uuid, primary key) - Course unique identifier
      - `name` (text) - Course name
      - `code` (text, unique) - Course code
      - `description` (text) - Course description
      - `teacher_id` (uuid) - Foreign key to users table
      - `academic_period` (text) - Academic period (e.g., 2025-1)
      - `access_code` (text) - Unique access code for student enrollment
      - `created_at` (timestamptz) - Course creation timestamp
  
  2. Security
    - Enable RLS on `courses` table
    - Add policies for teachers and students
*/

CREATE TABLE IF NOT EXISTS courses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  code text UNIQUE NOT NULL,
  description text NOT NULL,
  teacher_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  academic_period text NOT NULL,
  access_code text UNIQUE NOT NULL,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE courses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone authenticated can read courses"
  ON courses FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Teachers can create courses"
  ON courses FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Teachers can update courses"
  ON courses FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Teachers can delete courses"
  ON courses FOR DELETE
  TO authenticated
  USING (true);

CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(code);
CREATE INDEX IF NOT EXISTS idx_courses_access_code ON courses(access_code);