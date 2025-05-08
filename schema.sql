-- 1. Admins
CREATE TABLE
  admins (
    admin_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- store a bcrypt hash
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now (),
    updated_at TIMESTAMP NOT NULL DEFAULT now ()
  );

-- 2. Instructors
CREATE TABLE
  instructors (
    instructor_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now (),
    updated_at TIMESTAMP NOT NULL DEFAULT now ()
  );

-- 3. Students
CREATE TABLE
  students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE, -- optional
    face_template BYTEA, -- encrypted template blob
    student_number INT UNIQUE NOT NULL, -- e.g. university ID
    department VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT now (),
    updated_at TIMESTAMP NOT NULL DEFAULT now ()
  );

-- 4. Classrooms
CREATE TABLE
  classrooms (
    classroom_id SERIAL PRIMARY KEY,
    instructor_id INT REFERENCES instructors (instructor_id),
    name VARCHAR(255) NOT NULL,
    year INT NOT NULL,
    semester VARCHAR(10) NOT NULL CHECK (semester IN ('fall', 'spring', 'summer')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT now (),
    updated_at TIMESTAMP NOT NULL DEFAULT now (),
    UNIQUE (name, year, semester)
  );

-- 5. Classroom Enrollments
CREATE TABLE
  classroom_enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    classroom_id INT NOT NULL REFERENCES classrooms (classroom_id),
    student_id INT NOT NULL REFERENCES students (student_id),
    created_at TIMESTAMP NOT NULL DEFAULT now (),
    updated_at TIMESTAMP NOT NULL DEFAULT now (),
    UNIQUE (classroom_id, student_id)
  );

-- 6. Class Sessions
CREATE TABLE
  class_sessions (
    session_id SERIAL PRIMARY KEY,
    classroom_id INT NOT NULL REFERENCES classrooms (classroom_id),
    session_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now (),
    updated_at TIMESTAMP NOT NULL DEFAULT now (),
    UNIQUE (classroom_id, session_date, start_time)
  );

-- 7. Attendances
CREATE TABLE
  attendances (
    attendance_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES class_sessions (session_id),
    student_id INT NOT NULL REFERENCES students (student_id),
    status VARCHAR(10) NOT NULL CHECK (status IN ('absent', 'present')),
    marked_by VARCHAR(20) NOT NULL CHECK (marked_by IN ('system', 'instructor')),
    created_at TIMESTAMP NOT NULL DEFAULT now (),
    updated_at TIMESTAMP NOT NULL DEFAULT now (),
    UNIQUE (session_id, student_id)
  );