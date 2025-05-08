#!/usr/bin/env python3
# register_face.py

import os
import sys
import base64

import face_recognition
import psycopg2
from cryptography.fernet import Fernet

# —————————————————————————————————————————————————————————————
# Configuration (hard‑coded)
# —————————————————————————————————————————————————————————————

DB_HOST       = "127.0.0.1"
DB_NAME       = "snapattend"
DB_USER       = "mhmd"
DB_PASS       = "1234"
DB_PORT       = "5432"

KEY_FILE      = "face_key.key"

# —————————————————————————————————————————————————————————————
# Helper: load or create Fernet key
# —————————————————————————————————————————————————————————————

def get_fernet_key(key_file: str) -> bytes:
    if os.path.exists(key_file):
        return open(key_file, "rb").read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        print(f"[INFO] Generated new Fernet key → {key_file}")
        return key

fernet = Fernet(get_fernet_key(KEY_FILE))

# —————————————————————————————————————————————————————————————
# DB Connection
# —————————————————————————————————————————————————————————————

def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

# —————————————————————————————————————————————————————————————
# Main logic
# —————————————————————————————————————————————————————————————

def register_face(student_number: int, student_name: str, image_path: str):
    # 1) Load & encode face
    print(f"[INFO] Loading image: {image_path}")
    image = face_recognition.load_image_file(image_path)
    locs = face_recognition.face_locations(image, model="hog")
    if not locs:
        print("[ERROR] No face found in the image.")
        return
    encoding = face_recognition.face_encodings(image, [locs[0]])[0]

    # 2) Encrypt encoding
    raw = base64.b64encode(encoding.tobytes())
    encrypted = fernet.encrypt(raw)

    # 3) Connect & upsert student
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            # Try update first
            cur.execute("""
                UPDATE students
                SET name         = %s,
                    face_template= %s,
                    updated_at   = now()
                WHERE student_number = %s
                RETURNING student_id
            """, (student_name, psycopg2.Binary(encrypted), student_number))

            row = cur.fetchone()
            if row:
                student_id = row[0]
                print(f"[INFO] Updated existing student_id={student_id}")
            else:
                # Insert new
                cur.execute("""
                    INSERT INTO students (name, student_number, face_template)
                    VALUES (%s, %s, %s)
                    RETURNING student_id
                """, (student_name, student_number, psycopg2.Binary(encrypted)))
                student_id = cur.fetchone()[0]
                print(f"[INFO] Inserted new student_id={student_id}")

            conn.commit()

            # 4) Fetch all active classrooms
            cur.execute("""
                SELECT classroom_id
                  FROM classrooms
                WHERE is_active = TRUE
            """)
            classroom_ids = [cid for (cid,) in cur.fetchall()]
            print(f"[INFO] Found {len(classroom_ids)} active classrooms")

            # 5) Enroll into each classroom
            for cid in classroom_ids:
                cur.execute("""
                    INSERT INTO classroom_enrollments (classroom_id, student_id)
                    VALUES (%s, %s)
                    ON CONFLICT (classroom_id, student_id) DO NOTHING
                """, (cid, student_id))

            conn.commit()
            print(f"[INFO] Student_id={student_id} enrolled in all classrooms")

    except Exception as err:
        conn.rollback()
        print(f"[ERROR] Database error: {err}")
    finally:
        conn.close()

# —————————————————————————————————————————————————————————————
# CLI Entry
# —————————————————————————————————————————————————————————————

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: register_face.py <student_number> <student_name> <image_path>")
        sys.exit(1)

    snum     = int(sys.argv[1])
    sname    = sys.argv[2]
    img_path = sys.argv[3]
    register_face(snum, sname, img_path)
