/*
  # Create enrollments table for academic management system

  1. New Tables
    - `enrollments`
      - `id` (uuid, primary key) - Enrollment unique identifier
      - `student_id` (uuid) - Foreign key to users table
      - `course_id` (uuid) - Foreign key to courses table
      - `enrolled_at` (timestamptz) - Enrollment timestamp
  
  2. Security
    - Enable RLS on `enrollments` table
    - Add policies for students and teachers
*/

CREATE TABLE IF NOT EXISTS enrollments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  course_id uuid NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  enrolled_at timestamptz DEFAULT now(),
  UNIQUE(student_id, course_id)
);

ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone authenticated can read enrollments"
  ON enrollments FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Students can create enrollments"
  ON enrollments FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);