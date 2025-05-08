import cv2
import numpy as np
import base64
from typing import List, Tuple, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FaceRecognition:
    def __init__(self):
        # Initialize face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        # Initialize face recognition model
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()

        # Recognition threshold - adjust as needed
        self.confidence_threshold = 70.0

    def detect_faces(self, image: np.ndarray) -> List[np.ndarray]:
        """Detect faces in an image and return face crops"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        face_crops = []
        for x, y, w, h in faces:
            face_crops.append(gray[y : y + h, x : x + w])

        return face_crops

    def create_face_template(self, image_data: str) -> Optional[bytes]:
        """Create a face template from base64 encoded image"""
        try:
            # Decode base64 image
            img_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logger.error("Failed to decode image")
                return None

            # Detect faces
            faces = self.detect_faces(img)

            if not faces:
                logger.error("No face detected in the image")
                return None

            # We'll use the first detected face (can be improved to select best face)
            face = faces[0]

            # Create and pickle the face template
            # For real implementation, consider using more advanced features like face embeddings
            # This is a simplified example using raw pixel values
            return face.tobytes()

        except Exception as e:
            logger.error(f"Error creating face template: {e}")
            return None

    def compare_faces(self, face: np.ndarray, template: bytes) -> Tuple[bool, float]:
        """Compare a face with a stored template"""
        try:
            # Convert template bytes back to numpy array
            template_shape = (face.shape[0], face.shape[1])  # Assuming same shape
            template_face = np.frombuffer(template, dtype=np.uint8).reshape(
                template_shape
            )

            # Compute similarity score (lower is better)
            # For production, use a more robust method like face embeddings and cosine similarity
            diff = cv2.absdiff(face, template_face)
            similarity_score = np.sum(diff) / (face.shape[0] * face.shape[1])

            # Convert to confidence (higher is better)
            confidence = 100 - min(similarity_score, 100)

            return confidence > self.confidence_threshold, confidence

        except Exception as e:
            logger.error(f"Error comparing faces: {e}")
            return False, 0.0

    def process_attendance_image(
        self, image_data: str, student_templates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process an image and identify students for attendance"""
        try:
            # Decode base64 image
            img_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logger.error("Failed to decode image")
                return []

            # Detect faces
            faces = self.detect_faces(img)

            if not faces:
                logger.warning("No faces detected in the image")
                return []

            results = []

            # Compare each detected face with student templates
            for face in faces:
                best_match = None
                best_confidence = 0

                for student in student_templates:
                    # Skip students without face template
                    if not student["face_template"]:
                        continue

                    is_match, confidence = self.compare_faces(
                        face, student["face_template"]
                    )

                    if is_match and confidence > best_confidence:
                        best_confidence = confidence
                        best_match = student

                if best_match:
                    results.append(
                        {
                            "student_id": best_match["student_id"],
                            "student_name": best_match["name"],
                            "confidence": best_confidence,
                        }
                    )

            return results

        except Exception as e:
            logger.error(f"Error processing attendance image: {e}")
            return []


# Singleton instance
face_recognition = FaceRecognition()
