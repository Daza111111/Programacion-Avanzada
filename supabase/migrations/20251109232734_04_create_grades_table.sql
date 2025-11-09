/*
  # Create grades table for academic management system

  1. New Tables
    - `grades`
      - `id` (uuid, primary key) - Grade unique identifier
      - `enrollment_id` (uuid, unique) - Foreign key to enrollments table
      - `course_id` (uuid) - Foreign key to courses table
      - `student_id` (uuid) - Foreign key to users table
      - `student_name` (text) - Student's name for quick reference
      - `corte1` (numeric, nullable) - Grade for first cut (30%)
      - `corte2` (numeric, nullable) - Grade for second cut (35%)
      - `corte3` (numeric, nullable) - Grade for third cut (35%)
      - `final_grade` (numeric, nullable) - Calculated final grade
      - `last_updated` (timestamptz) - Last update timestamp
  
  2. Security
    - Enable RLS on `grades` table
    - Add policies for students and teachers
*/

CREATE TABLE IF NOT EXISTS grades (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  enrollment_id uuid UNIQUE NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
  course_id uuid NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  student_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  student_name text NOT NULL,
  corte1 numeric(3,1) CHECK (corte1 >= 0 AND corte1 <= 5),
  corte2 numeric(3,1) CHECK (corte2 >= 0 AND corte2 <= 5),
  corte3 numeric(3,1) CHECK (corte3 >= 0 AND corte3 <= 5),
  final_grade numeric(3,2) CHECK (final_grade >= 0 AND final_grade <= 5),
  last_updated timestamptz DEFAULT now()
);

ALTER TABLE grades ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone authenticated can read grades"
  ON grades FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Anyone authenticated can create grades"
  ON grades FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Anyone authenticated can update grades"
  ON grades FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_grades_enrollment_id ON grades(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_grades_course_id ON grades(course_id);
CREATE INDEX IF NOT EXISTS idx_grades_student_id ON grades(student_id);