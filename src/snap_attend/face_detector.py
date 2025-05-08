"""
Face Attendance System - Refactored Implementation
"""
import cv2
import face_recognition
import numpy as np
import json
import os
import logging
import datetime
import psycopg2
import bcrypt
import base64
from cryptography.fernet import Fernet
from psycopg2.extras import DictCursor
import argparse 

# Configuration and logging utilities extracted from the class
def load_config(config_file="../../config.json"):
    """Load configuration from JSON file."""
    default_config = {
        "input_source": "camera",  # "camera" or path to image
        "camera_id": 0,
        "output_dir": "attendance_images",
        "use_histogram_equalization": True,
        "use_gamma_correction": True,
        "gamma_value": 0.8,
        "face_detection_model": "hog",  # "hog" (faster) or "cnn" (more accurate)
        "recognition_tolerance": 0.6,  # Lower is stricter matching
        "save_attendance_images": True,
        "database": {
            "host": "localhost",
            "dbname": "attendance_db",
            "user": "postgres",
            "password": "password",
            "port": 5432
        },
        "logging": {
            "level": "INFO",
            "file": "face_attendance.log",
            "console": True,
            "format": "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
        }
    }
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            # Set up basic logging to report config loading
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
            logging.info(f"Configuration loaded from '{config_file}'")
            
            # Merge with defaults for any missing keys
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
                elif isinstance(value, dict) and isinstance(config[key], dict):
                    for subkey, subvalue in value.items():
                        if subkey not in config[key]:
                            config[key][subkey] = subvalue
                            
            return config
    except FileNotFoundError:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
        logging.warning(f"Config file '{config_file}' not found. Using default settings.")
        return default_config
    except json.JSONDecodeError:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
        logging.error(f"Invalid JSON in config file '{config_file}'. Using default settings.")
        return default_config

def setup_logging(config):
    """Configure logging based on settings."""
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_format = log_config.get("format", "%(asctime)s - %(levelname)s - %(message)s")
    log_file = log_config.get("file", "face_attendance.log")
    console_output = log_config.get("console", True)
    
    # Create logger
    logger = logging.getLogger("face_attendance")
    logger.setLevel(log_level)
    logger.handlers = []  # Clear any existing handlers
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Add file handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add console handler if enabled
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def get_encryption_key(config):
    """Get or create encryption key for face templates."""
    key_file = config.get("encryption_key_file", "face_key.key")
    logger = logging.getLogger("face_attendance")
    
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    else:
        # Generate a new key
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        logger.info(f"Generated new encryption key and saved to {key_file}")
        return key


# Face Detection Module - Separated from recognition
class FaceDetector:
    """Handles face detection in images."""
    
    def __init__(self, config):
        """Initialize the face detector with configuration."""
        self.config = config
        self.logger = logging.getLogger("face_attendance")
        self.detection_model = config.get("face_detection_model", "hog")
    
    def apply_gamma_correction(self, image, gamma=1.0):
        """Apply gamma correction to the image."""
        # Build a lookup table mapping pixel values [0, 255] to adjusted gamma values
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
        # Apply gamma correction using the lookup table
        return cv2.LUT(image, table)
    
    def preprocess_image(self, image):
        """Preprocess image before face detection."""
        # Make a copy for processing
        processed_image = image.copy()
        
        # Apply histogram equalization if enabled
        if self.config.get("use_histogram_equalization", True):
            self.logger.debug("Applying histogram equalization")
            try:
                # Convert to grayscale for histogram equalization
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # Apply histogram equalization
                equalized_gray = cv2.equalizeHist(gray_image)
                self.logger.debug("Histogram equalization completed")
            except Exception as e:
                self.logger.error(f"Error during histogram equalization: {str(e)}")
        
        # Apply gamma correction if enabled
        if self.config.get("use_gamma_correction", True):
            gamma_value = self.config.get("gamma_value", 0.8)
            self.logger.debug(f"Applying gamma correction with gamma={gamma_value}")
            try:
                processed_image = self.apply_gamma_correction(processed_image, gamma=gamma_value)
                self.logger.debug("Gamma correction completed")
            except Exception as e:
                self.logger.error(f"Error during gamma correction: {str(e)}")
        
        return processed_image
    
    def detect_faces(self, image):
        """Detect faces in the image and return their locations and encodings."""
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Convert BGR to RGB (face_recognition works with RGB)
            rgb_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
            
            # Detect face locations
            self.logger.debug("Detecting faces")
            face_locations = face_recognition.face_locations(
                rgb_image, 
                model=self.detection_model
            )
            self.logger.info(f"Found {len(face_locations)} faces")
            
            if not face_locations:
                return processed_image, [], []
                
            # Generate face encodings for detected faces
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            return processed_image, face_locations, face_encodings
            
        except Exception as e:
            self.logger.error(f"Error detecting faces: {str(e)}", exc_info=True)
            return image, [], []


# Face Recognition Module
class FaceRecognizer:
    """Handles face recognition and comparing with known faces."""
    
    def __init__(self, config):
        """Initialize the face recognizer."""
        self.config = config
        self.logger = logging.getLogger("face_attendance")
        self.recognition_tolerance = config.get("recognition_tolerance", 0.6)
    
    def recognize_faces(self, face_encodings, known_students):
        """Compare detected faces with known faces to identify students."""
        recognized_students = []
        
        # If no known students, return all as unknown
        if not known_students or not face_encodings:
            return [{"student_id": None, "name": "Unknown", "recognized": False} for _ in face_encodings]
        
        # Extract just the face encodings for comparison
        known_face_encodings = [s['face_encoding'] for s in known_students]
        
        for face_encoding in face_encodings:
            # Default name is "Unknown"
            name = "Unknown"
            student_id = None
            match_found = False
            
            # Compare face with known faces
            matches = face_recognition.compare_faces(
                known_face_encodings, 
                face_encoding,
                tolerance=self.recognition_tolerance
            )
            
            # Get distances to all known faces
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            
            confidence = None
            if any(matches):
                # Get the index of the best (smallest) distance
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    student = known_students[best_match_index]
                    name = student['name']
                    student_id = student['student_id']
                    match_found = True
                    # Convert distance to a simple "confidence" score (closer = higher confidence)
                    confidence = 1.0 - float(face_distances[best_match_index])

            
            # Add to recognized students list
            recognized_students.append({
                'student_id': student_id, 
                'name': name,
                'recognized': match_found,
                'confidence': confidence
            })
                
        return recognized_students


# Database Module
class DatabaseManager:
    """Handles database operations for the attendance system."""
    
    def __init__(self, config):
        """Initialize database manager with configuration."""
        self.config = config
        self.logger = logging.getLogger("face_attendance")
        self.db_conn = None
        
        # Initialize encryption
        self.encryption_key = get_encryption_key(config)
        self.fernet = Fernet(self.encryption_key)
    
    def connect_to_db(self):
        """Connect to the PostgreSQL database."""
        if self.db_conn is not None and not self.db_conn.closed:
            return self.db_conn
            
        try:
            db_config = self.config.get("database", {})
            self.db_conn = psycopg2.connect(
                host=db_config.get("host", "localhost"),
                dbname=db_config.get("dbname", "attendance_db"),
                user=db_config.get("user", "postgres"),
                password=db_config.get("password", "password"),
                port=db_config.get("port", 5432)
            )
            self.logger.info("Successfully connected to the database")
            return self.db_conn
        except Exception as e:
            self.logger.error(f"Database connection error: {str(e)}")
            raise
    
    def close_db_connection(self):
        """Close the database connection."""
        if self.db_conn is not None and not self.db_conn.closed:
            self.db_conn.close()
            self.logger.info("Database connection closed")
    
    def encrypt_face_encoding(self, face_encoding):
        """Encrypt face encoding for secure storage."""
        # Convert numpy array to bytes
        face_bytes = base64.b64encode(face_encoding.tobytes())
        # Encrypt the bytes
        encrypted_data = self.fernet.encrypt(face_bytes)
        return encrypted_data

    def decrypt_face_encoding(self, encrypted_data):
        """Decrypt face encoding from database."""
        try:
            # If it's coming from psycopg2 as a memoryview or similar, convert to bytes
            if not isinstance(encrypted_data, (str, bytes)):
                encrypted_data = bytes(encrypted_data)
                
            # Decrypt the data
            decrypted_bytes = self.fernet.decrypt(encrypted_data)
            
            # Convert back to numpy array
            face_array = np.frombuffer(base64.b64decode(decrypted_bytes), dtype=np.float64)
            return face_array
        except Exception as e:
            self.logger.error(f"Error decrypting face encoding: {str(e)}")
            return None
    
    def get_all_student_face_encodings(self, classroom_id=None):
        """Retrieve all student face encodings from the database, optionally filtered by classroom."""
        try:
            conn = self.connect_to_db()
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                if classroom_id is not None:
                    # Get faces for students in a specific classroom
                    query = """
                    SELECT s.student_id, s.name, s.face_template 
                    FROM students s
                    JOIN classroom_enrollments ce ON s.student_id = ce.student_id
                    WHERE ce.classroom_id = %s AND s.face_template IS NOT NULL
                    """
                    cursor.execute(query, (classroom_id,))
                else:
                    # Get all student faces
                    cursor.execute(
                        "SELECT student_id, name, face_template FROM students WHERE face_template IS NOT NULL"
                    )
                
                students = cursor.fetchall()
                
            # Process and return student data with decrypted face encodings
            result = []
            for student in students:
                if student['face_template']:
                    face_encoding = self.decrypt_face_encoding(student['face_template'])
                    if face_encoding is not None:
                        result.append({
                            'student_id': student['student_id'],
                            'name': student['name'],
                            'face_encoding': face_encoding
                        })
            
            self.logger.info(f"Retrieved {len(result)} student face encodings")
            return result
            
        except Exception as e:
            self.logger.error(f"Error retrieving student face encodings: {str(e)}")
            return []
    
    def register_student_face(self, student_id, image_path):
        """Register a student's face in the database."""
        try:
            # Load image and detect face
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image, model=self.config["face_detection_model"])
            
            if not face_locations:
                self.logger.warning(f"No face detected in the image for student {student_id}")
                return False
                
            if len(face_locations) > 1:
                self.logger.warning(f"Multiple faces detected in the image for student {student_id}. Using the first one.")
                
            # Generate face encoding
            face_encoding = face_recognition.face_encodings(image, [face_locations[0]])[0]
            
            # Encrypt the face encoding
            encrypted_encoding = self.encrypt_face_encoding(face_encoding)
            
            # Update student record in database
            conn = self.connect_to_db()
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE students SET face_template = %s, updated_at = now() WHERE student_id = %s",
                    (encrypted_encoding, student_id)
                )
                conn.commit()
                
            self.logger.info(f"Successfully registered face for student {student_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering student face: {str(e)}")
            return False
    
    def record_attendance(self, session_id, student_id, status="present"):
        """Record a student's attendance for a class session."""
        try:
            conn = self.connect_to_db()
            with conn.cursor() as cursor:
                # Check if attendance record already exists
                cursor.execute(
                    "SELECT attendance_id FROM attendances WHERE session_id = %s AND student_id = %s",
                    (session_id, student_id)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute(
                        "UPDATE attendances SET status = %s, marked_by = 'system', updated_at = now() WHERE session_id = %s AND student_id = %s",
                        (status, session_id, student_id)
                    )
                else:
                    # Create new record
                    cursor.execute(
                        "INSERT INTO attendances (session_id, student_id, status, marked_by) VALUES (%s, %s, %s, 'system')",
                        (session_id, student_id, status)
                    )
                conn.commit()
                
            self.logger.info(f"Recorded {status} attendance for student {student_id} in session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording attendance: {str(e)}")
            return False
    
    def get_active_class_sessions(self):
        """Get active class sessions based on current time."""
        try:
            current_time = datetime.datetime.now().time()
            current_date = datetime.date.today()
            
            conn = self.connect_to_db()
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = """
                SELECT cs.session_id, cs.classroom_id, c.name as classroom_name, 
                       cs.start_time, cs.end_time
                FROM class_sessions cs
                JOIN classrooms c ON cs.classroom_id = c.classroom_id
                WHERE cs.session_date = %s 
                AND cs.start_time <= %s 
                AND cs.end_time >= %s
                AND c.is_active = TRUE
                """
                cursor.execute(query, (current_date, current_time, current_time))
                active_sessions = cursor.fetchall()
                
            self.logger.info(f"Found {len(active_sessions)} active class sessions")
            return active_sessions
            
        except Exception as e:
            self.logger.error(f"Error retrieving active class sessions: {str(e)}")
            return []
    
    def get_current_class_session_by_classroom(self, classroom_id):
        """Get current class session for a specific classroom."""
        try:
            current_time = datetime.datetime.now().time()
            current_date = datetime.date.today()
            
            conn = self.connect_to_db()
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query = """
                SELECT session_id, classroom_id, session_date, start_time, end_time
                FROM class_sessions 
                WHERE classroom_id = %s
                AND session_date = %s 
                AND start_time <= %s 
                AND end_time >= %s
                """
                cursor.execute(query, (classroom_id, current_date, current_time, current_time))
                session = cursor.fetchone()
                
            if session:
                self.logger.info(f"Found active session {session['session_id']} for classroom {classroom_id}")
                return dict(session)
            else:
                self.logger.info(f"No active session found for classroom {classroom_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving current class session: {str(e)}")
            return None


# Main Attendance System Class - Now slimmer and more focused
class FaceAttendanceSystem:
    """Main class for the face attendance system."""
    
    def __init__(self, config_file="config.json"):
        """Initialize the face attendance system components."""
        # Load configuration
        self.config = load_config(config_file)
        # Set up logging
        self.logger = setup_logging(self.config)
        
        # Initialize components
        self.db_manager = DatabaseManager(self.config)
        self.face_detector = FaceDetector(self.config)
        self.face_recognizer = FaceRecognizer(self.config)
    
    def process_image(self, image, session_id=None):
        """Process an image to detect, recognize faces and record attendance."""
        try:
            # Detect faces
            processed_image, face_locations, face_encodings = self.face_detector.detect_faces(image)
            
            if not face_locations:
                self.logger.info("No faces detected in the image")
                return processed_image, []
            
            # Get student face encodings from database
            classroom_id = None
            if session_id:
                # Get classroom_id from session_id
                conn = self.db_manager.connect_to_db()
                with conn.cursor() as cursor:
                    cursor.execute("SELECT classroom_id FROM class_sessions WHERE session_id = %s", (session_id,))
                    result = cursor.fetchone()
                    if result:
                        classroom_id = result[0]
                
            known_students = self.db_manager.get_all_student_face_encodings(classroom_id)
            
            # Recognize faces
            recognized_students = self.face_recognizer.recognize_faces(face_encodings, known_students)
            
            # Add face locations to recognized students for drawing
            for i, student in enumerate(recognized_students):
                student['location'] = face_locations[i]
            
            # Record attendance if session_id is provided
            if session_id is not None:
                for student in recognized_students:
                    if student['recognized']:
                        self.db_manager.record_attendance(session_id, student['student_id'])
            
            # Draw face rectangles and names on the image
            for student in recognized_students:
                top, right, bottom, left = student['location']
                
                # Determine color based on recognition status
                color = (0, 255, 0) if student['recognized'] else (0, 0, 255)  # Green if matched, red if unknown
                
                # Draw rectangle and name
                cv2.rectangle(processed_image, (left, top), (right, bottom), color, 2)
                
                # Add confidence if recognized
                display_text = student['name']
                if student['recognized']:
                    display_text += f" ({student['confidence']:.2f})"
                
                cv2.putText(
                    processed_image, 
                    display_text, 
                    (left, bottom + 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, 
                    color, 
                    1, 
                    cv2.LINE_AA
                )
            
            return processed_image, recognized_students
            
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}", exc_info=True)
            return image, []
    
    def process_single_image(self, image_path, session_id=None):
        """Process a single image file for attendance tracking."""
        try:
            # Load image file
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Could not read image file: {image_path}")
                return None, []
                
            self.logger.info(f"Processing image: {image_path}")
            
            # Process the image
            processed_image, recognized_students = self.process_image(image, session_id)
            
            # Save the processed image if configured
            if self.config.get("save_attendance_images", True):
                output_dir = self.config.get("output_dir", "attendance_images")
                os.makedirs(output_dir, exist_ok=True)
                
                filename = os.path.basename(image_path)
                base_name, ext = os.path.splitext(filename)
                
                output_path = os.path.join(
                    output_dir, 
                    f"{base_name}_processed{ext}"
                )
                
                cv2.imwrite(output_path, processed_image)
                self.logger.info(f"Saved processed image to {output_path}")
            
            # Log recognition results
            recognized_count = sum(1 for s in recognized_students if s['recognized'])
            self.logger.info(f"Recognized {recognized_count} out of {len(recognized_students)} detected faces")
            
            for student in recognized_students:
                if student['recognized']:
                    self.logger.info(f"Recognized {student['name']} (ID: {student['student_id']}) with confidence {student['confidence']:.2f}")
                else:
                    self.logger.info(f"Unknown face detected at {student['location']}")
            
            return processed_image, recognized_students
            
        except Exception as e:
            self.logger.error(f"Error processing image file: {str(e)}", exc_info=True)
            return None, []
    
    def process_image_folder(self, folder_path, session_id=None):
        """Process all images in a folder for attendance tracking."""
        try:
            self.logger.info(f"Processing images in folder: {folder_path}")
            
            # Check if folder exists
            if not os.path.isdir(folder_path):
                self.logger.error(f"Folder not found: {folder_path}")
                return
            
            # Get all image files in the folder
            valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
            image_files = [
                os.path.join(folder_path, f) for f in os.listdir(folder_path)
                if os.path.splitext(f.lower())[1] in valid_extensions
            ]
            
            if not image_files:
                self.logger.warning(f"No image files found in {folder_path}")
                return
            
            self.logger.info(f"Found {len(image_files)} image files")
            
            # Process each image
            results = []
            for image_path in image_files:
                processed_image, recognized_students = self.process_single_image(image_path, session_id)
                if processed_image is not None:
                    results.append((image_path, recognized_students))
            
            # Summarize results
            if results:
                total_faces = sum(len(r[1]) for r in results)
                total_recognized = sum(sum(1 for s in r[1] if s['recognized']) for r in results)
                
                self.logger.info(f"Summary: Processed {len(results)} images")
                self.logger.info(f"Total faces detected: {total_faces}")
                self.logger.info(f"Total faces recognized: {total_recognized}")
                
                # Generate attendance summary by student
                if session_id is not None:
                    student_attendance = {}
                    for _, students in results:
                        for student in students:
                            if student['recognized']:
                                student_id = student['student_id']
                                if student_id not in student_attendance:
                                    student_attendance[student_id] = {
                                        'name': student['name'],
                                        'count': 0
                                    }
                                student_attendance[student_id]['count'] += 1
                    
                    self.logger.info(f"Attendance summary for session {session_id}:")
                    for student_id, data in student_attendance.items():
                        self.logger.info(f"  {data['name']} (ID: {student_id}): detected {data['count']} times")
            
            return results
                
        except Exception as e:
            self.logger.error(f"Error processing image folder: {str(e)}", exc_info=True)
            return []
    
    def close(self):
        """Clean up resources used by the system."""
        self.db_manager.close_db_connection()
        self.logger.info("Face attendance system shut down")


def main():
    """Main function to run the attendance system."""
    parser = argparse.ArgumentParser(description="Face Attendance System")
    parser.add_argument("--image", "-i", type=str, help="Path to a single image file to process")
    parser.add_argument("--folder", "-f", type=str, help="Path to a folder of images to process")
    parser.add_argument("--classroom", "-c", type=int, help="Classroom ID to track attendance for")
    parser.add_argument("--session", "-s", type=int, help="Session ID to record attendance for")
    parser.add_argument("--config", type=str, default="../../config.json", help="Path to config file")
    args = parser.parse_args()
    
    system = FaceAttendanceSystem(config_file=args.config)
    
    try:
        # Get session ID if classroom is provided but session is not
        session_id = args.session
        if session_id is None and args.classroom is not None:
            session = system.db_manager.get_current_class_session_by_classroom(args.classroom)
            if session:
                session_id = session['session_id']
                system.logger.info(f"Using active session {session_id} for classroom {args.classroom}")
            else:
                system.logger.warning(f"No active session found for classroom {args.classroom}")
                return
        
        # Process image(s)
        if args.image:
            # Process a single image
            system.process_single_image(args.image, session_id)
        elif args.folder:
            # Process all images in a folder
            system.process_image_folder(args.folder, session_id)
        else:
            system.logger.error("No input specified. Use --image or --folder to specify input.")
            
    except KeyboardInterrupt:
        system.logger.info("Interrupted by user")
    finally:
        system.close()

if __name__ == "__main__":
    main()
