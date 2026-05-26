"""
Face Detection Module using OpenCV
Detects faces in images using Haar Cascade or DNN methods
"""

import cv2
import numpy as np
import os
from django.conf import settings


class FaceDetector:
    """
    Face detector using OpenCV with multiple detection methods
    """
    
    def __init__(self, method='haar'):
        """
        Initialize face detector
        
        Args:
            method: Detection method ('haar' or 'dnn')
        """
        self.method = method
        self.face_cascade = None
        self.dnn_net = None
        
        if method == 'haar':
            self._load_haar_cascade()
        elif method == 'dnn':
            self._load_dnn_model()
    
    def _load_haar_cascade(self):
        """Load Haar Cascade classifier"""
        try:
            # Try to load from OpenCV data
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                raise Exception("Failed to load Haar Cascade")
                
        except Exception as e:
            print(f"Error loading Haar Cascade: {e}")
            # Fallback to alternative path
            alt_path = os.path.join(
                os.path.dirname(__file__),
                'models',
                'haarcascade_frontalface_default.xml'
            )
            if os.path.exists(alt_path):
                self.face_cascade = cv2.CascadeClassifier(alt_path)
    
    def _load_dnn_model(self):
        """Load DNN face detection model"""
        try:
            model_dir = os.path.join(os.path.dirname(__file__), 'models')
            prototxt_path = os.path.join(model_dir, 'deploy.prototxt')
            model_path = os.path.join(model_dir, 'res10_300x300_ssd_iter_140000.caffemodel')
            
            if os.path.exists(prototxt_path) and os.path.exists(model_path):
                self.dnn_net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
            else:
                print("DNN model files not found, falling back to Haar Cascade")
                self._load_haar_cascade()
                self.method = 'haar'
        except Exception as e:
            print(f"Error loading DNN model: {e}")
            self._load_haar_cascade()
            self.method = 'haar'
    
    def detect_faces(self, image, min_confidence=0.5):
        """
        Detect faces in an image
        
        Args:
            image: Input image (numpy array or file path)
            min_confidence: Minimum confidence for DNN detection
            
        Returns:
            List of face bounding boxes [(x, y, w, h), ...]
        """
        # Load image if path is provided
        if isinstance(image, str):
            image = cv2.imread(image)
        
        if image is None:
            return []
        
        # Convert to grayscale for Haar Cascade
        if self.method == 'haar':
            return self._detect_haar(image)
        elif self.method == 'dnn':
            return self._detect_dnn(image, min_confidence)
        
        return []
    
    def _detect_haar(self, image):
        """Detect faces using Haar Cascade"""
        if self.face_cascade is None:
            return []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return [tuple(map(int, face)) for face in faces]
    
    def _detect_dnn(self, image, min_confidence=0.5):
        """Detect faces using DNN"""
        if self.dnn_net is None:
            return self._detect_haar(image)
        
        (h, w) = image.shape[:2]
        
        # Prepare blob for DNN
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )
        
        # Pass through network
        self.dnn_net.setInput(blob)
        detections = self.dnn_net.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > min_confidence:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x, y, x2, y2) = box.astype("int")
                
                # Convert to (x, y, w, h) format
                faces.append((x, y, x2 - x, y2 - y))
        
        return faces
    
    def extract_face(self, image, face_box, target_size=(48, 48), grayscale=True):
        """
        Extract and preprocess face region
        
        Args:
            image: Input image
            face_box: Face bounding box (x, y, w, h)
            target_size: Target size for face image
            grayscale: Convert to grayscale
            
        Returns:
            Preprocessed face image
        """
        x, y, w, h = face_box
        
        # Extract face region
        face = image[y:y+h, x:x+w]
        
        if face.size == 0:
            return None
        
        # Convert to grayscale if needed
        if grayscale and len(face.shape) == 3:
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        
        # Resize to target size
        face = cv2.resize(face, target_size)
        
        return face
    
    def draw_faces(self, image, faces, labels=None, confidences=None):
        """
        Draw bounding boxes around detected faces
        
        Args:
            image: Input image
            faces: List of face bounding boxes
            labels: Optional list of emotion labels
            confidences: Optional list of confidence scores
            
        Returns:
            Image with drawn faces
        """
        output = image.copy()
        
        for i, (x, y, w, h) in enumerate(faces):
            # Draw rectangle
            cv2.rectangle(output, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Add label if provided
            if labels and i < len(labels):
                label = labels[i]
                if confidences and i < len(confidences):
                    label = f"{label}: {confidences[i]:.2%}"
                
                # Draw label background
                (label_w, label_h), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                cv2.rectangle(
                    output,
                    (x, y - label_h - 10),
                    (x + label_w, y),
                    (0, 255, 0),
                    -1
                )
                
                # Draw label text
                cv2.putText(
                    output,
                    label,
                    (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 0),
                    2
                )
        
        return output
    
    def get_largest_face(self, faces):
        """
        Get the largest face from detected faces
        
        Args:
            faces: List of face bounding boxes
            
        Returns:
            Largest face bounding box or None
        """
        if not faces:
            return None
        
        # Calculate area for each face
        areas = [w * h for (x, y, w, h) in faces]
        
        # Return face with largest area
        max_idx = areas.index(max(areas))
        return faces[max_idx]
    
    def preprocess_for_model(self, face_image):
        """
        Preprocess face image for emotion recognition model
        
        Args:
            face_image: Face image (grayscale)
            
        Returns:
            Preprocessed image ready for model input
        """
        # Normalize pixel values
        face_image = face_image.astype('float32') / 255.0
        
        # Expand dimensions for model input
        face_image = np.expand_dims(face_image, axis=-1)  # Add channel dimension
        face_image = np.expand_dims(face_image, axis=0)   # Add batch dimension
        
        return face_image


def load_image_from_base64(base64_string):
    """
    Load image from base64 string
    
    Args:
        base64_string: Base64 encoded image string
        
    Returns:
        OpenCV image (numpy array)
    """
    import base64
    
    # Remove data URL prefix if present
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    # Decode base64
    img_data = base64.b64decode(base64_string)
    
    # Convert to numpy array
    nparr = np.frombuffer(img_data, np.uint8)
    
    # Decode image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    return image


def save_image_from_base64(base64_string, output_path):
    """
    Save base64 image to file
    
    Args:
        base64_string: Base64 encoded image string
        output_path: Path to save image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        image = load_image_from_base64(base64_string)
        if image is not None:
            cv2.imwrite(output_path, image)
            return True
    except Exception as e:
        print(f"Error saving image: {e}")
    
    return False

# Made with Bob
