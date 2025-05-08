-- Admins
INSERT INTO
    admins (email, password_hash, name)
VALUES
    (
        'admin1@example.com',
        '$2a$12$pwSzzF1qrGvLn/AePI8UaOgbzqv5vk7e86CfGWkeAnB.4/1.Q7sBe',
        'Alice Admin'
    ),
    (
        'admin2@example.com',
        '$2a$12$pwSzzF1qrGvLn/AePI8UaOgbzqv5vk7e86CfGWkeAnB.4/1.Q7sBe',
        'Bob Boss'
    );

-- Instructors
INSERT INTO
    instructors (email, password_hash, name)
VALUES
    (
        'instructor1@example.edu',
        '$2a$12$pwSzzF1qrGvLn/AePI8UaOgbzqv5vk7e86CfGWkeAnB.4/1.Q7sBe',
        'John Doe'
    ),
    (
        'instructor2@example.edu',
        '$2a$12$pwSzzF1qrGvLn/AePI8UaOgbzqv5vk7e86CfGWkeAnB.4/1.Q7sBe',
        'Jane Smith'
    );

-- Students
INSERT INTO
    students (
        name,
        email,
        face_template,
        student_number,
        department
    )
VALUES
    (
        'Abdelrahman Mostafa',
        'abdelrahmanmostafa@student.edu',
        '\\xDEADBEEF',
        20230001,
        'Computer Science'
    ),
    (
        'Mohamed Hammoud',
        'mohameadhammoud@student.edu',
        '\\xDEADBEEF',
        20230002,
        'Electrical Engineering'
    ),
    (
        'Mohamed Anas Waqar',
        'mohamedanaswaqar@student.edu',
        '\\xDEADBEEF',
        20230003,
        'Mechanical Engineering'
    );

-- Classrooms
INSERT INTO
    classrooms (instructor_id, name, year, semester)
VALUES
    (1, 'CS101 - Intro to Programming', 2025, 'spring'),
    (2, 'EE201 - Circuit Analysis', 2025, 'spring');

-- Classroom Enrollments
INSERT INTO
    classroom_enrollments (classroom_id, student_id)
VALUES
    (1, 1),
    (1, 2),
    (1, 4),
    (1, 5),
    (2, 2),
    (2, 3);

-- Class Sessions
INSERT INTO
    class_sessions (classroom_id, session_date, start_time, end_time)
VALUES
    (1, '2025-05-01', '09:00', '10:30'),
    (1, '2025-05-03', '09:00', '10:30'),
    (2, '2025-05-02', '11:00', '12:30');

-- Attendances
INSERT INTO
    attendances (session_id, student_id, status, marked_by)
VALUES
    -- Session 1 (CS101)
    (1, 1, 'present', 'system'),
    (1, 2, 'absent', 'system'),
    (1, 4, 'present', 'system'),
    (1, 5, 'present', 'system'),
    -- Session 2 (CS101)
    (2, 1, 'present', 'instructor'),
    (2, 2, 'present', 'instructor'),
    (2, 4, 'absent', 'instructor'),
    (2, 5, 'present', 'instructor'),
    -- Session 3 (EE201)
    (3, 2, 'present', 'system'),
    (3, 3, 'absent', 'system');