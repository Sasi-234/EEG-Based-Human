"""
Image Preprocessing Utilities for Face Emotion Recognition
Handles image loading, preprocessing, and augmentation
"""

import cv2
import numpy as np
from PIL import Image
import io


def preprocess_face_image(image, target_size=(48, 48), grayscale=True, normalize=True):
    """
    Preprocess face image for emotion recognition
    
    Args:
        image: Input image (numpy array, PIL Image, or file path)
        target_size: Target size (width, height)
        grayscale: Convert to grayscale
        normalize: Normalize pixel values to [0, 1]
        
    Returns:
        Preprocessed image as numpy array
    """
    # Load image if path is provided
    if isinstance(image, str):
        image = cv2.imread(image)
    elif isinstance(image, Image.Image):
        image = np.array(image)
    
    if image is None:
        raise ValueError("Invalid image input")
    
    # Convert to grayscale if needed
    if grayscale:
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Resize to target size
    image = cv2.resize(image, target_size)
    
    # Normalize pixel values
    if normalize:
        image = image.astype('float32') / 255.0
    
    return image


def preprocess_for_model(image, target_size=(48, 48)):
    """
    Preprocess image specifically for the emotion recognition model
    
    Args:
        image: Input image
        target_size: Target size for model input
        
    Returns:
        Preprocessed image ready for model prediction
    """
    # Preprocess image
    processed = preprocess_face_image(image, target_size, grayscale=True, normalize=True)
    
    # Add channel dimension if grayscale
    if len(processed.shape) == 2:
        processed = np.expand_dims(processed, axis=-1)
    
    # Add batch dimension
    processed = np.expand_dims(processed, axis=0)
    
    return processed


def load_image_from_upload(uploaded_file):
    """
    Load image from Django uploaded file
    
    Args:
        uploaded_file: Django UploadedFile object
        
    Returns:
        OpenCV image (numpy array)
    """
    # Read file content
    file_bytes = uploaded_file.read()
    
    # Convert to numpy array
    nparr = np.frombuffer(file_bytes, np.uint8)
    
    # Decode image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    return image


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


def save_image_to_file(image, filepath):
    """
    Save image to file
    
    Args:
        image: OpenCV image (numpy array)
        filepath: Path to save image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cv2.imwrite(filepath, image)
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def enhance_image(image):
    """
    Enhance image quality for better face detection
    
    Args:
        image: Input image
        
    Returns:
        Enhanced image
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply histogram equalization
    enhanced = cv2.equalizeHist(gray)
    
    # Apply Gaussian blur to reduce noise
    enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
    
    return enhanced


def augment_image(image, rotation_range=20, shift_range=0.2, zoom_range=0.2, flip=True):
    """
    Apply data augmentation to image
    
    Args:
        image: Input image
        rotation_range: Range for random rotation (degrees)
        shift_range: Range for random shifts (fraction of size)
        zoom_range: Range for random zoom
        flip: Whether to randomly flip horizontally
        
    Returns:
        Augmented image
    """
    h, w = image.shape[:2]
    augmented = image.copy()
    
    # Random rotation
    if rotation_range > 0:
        angle = np.random.uniform(-rotation_range, rotation_range)
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
        augmented = cv2.warpAffine(augmented, M, (w, h))
    
    # Random shift
    if shift_range > 0:
        tx = np.random.uniform(-shift_range, shift_range) * w
        ty = np.random.uniform(-shift_range, shift_range) * h
        M = np.float32([[1, 0, tx], [0, 1, ty]])
        augmented = cv2.warpAffine(augmented, M, (w, h))
    
    # Random zoom
    if zoom_range > 0:
        zoom = np.random.uniform(1 - zoom_range, 1 + zoom_range)
        M = cv2.getRotationMatrix2D((w/2, h/2), 0, zoom)
        augmented = cv2.warpAffine(augmented, M, (w, h))
    
    # Random horizontal flip
    if flip and np.random.random() > 0.5:
        augmented = cv2.flip(augmented, 1)
    
    return augmented


def batch_preprocess(images, target_size=(48, 48)):
    """
    Preprocess multiple images at once
    
    Args:
        images: List of images
        target_size: Target size for all images
        
    Returns:
        Numpy array of preprocessed images
    """
    processed_images = []
    
    for image in images:
        processed = preprocess_face_image(image, target_size, grayscale=True, normalize=True)
        
        # Add channel dimension
        if len(processed.shape) == 2:
            processed = np.expand_dims(processed, axis=-1)
        
        processed_images.append(processed)
    
    return np.array(processed_images)


def crop_face_region(image, face_box, padding=0.2):
    """
    Crop face region from image with optional padding
    
    Args:
        image: Input image
        face_box: Face bounding box (x, y, w, h)
        padding: Padding around face (fraction of face size)
        
    Returns:
        Cropped face image
    """
    x, y, w, h = face_box
    
    # Calculate padding
    pad_w = int(w * padding)
    pad_h = int(h * padding)
    
    # Calculate crop coordinates with padding
    x1 = max(0, x - pad_w)
    y1 = max(0, y - pad_h)
    x2 = min(image.shape[1], x + w + pad_w)
    y2 = min(image.shape[0], y + h + pad_h)
    
    # Crop face region
    face = image[y1:y2, x1:x2]
    
    return face


def align_face(image, face_landmarks=None):
    """
    Align face based on eye positions (if landmarks available)
    
    Args:
        image: Input face image
        face_landmarks: Optional facial landmarks
        
    Returns:
        Aligned face image
    """
    # If no landmarks, return original image
    if face_landmarks is None:
        return image
    
    # This is a placeholder for face alignment
    # Full implementation would require facial landmark detection
    return image


def normalize_lighting(image):
    """
    Normalize lighting conditions in image
    
    Args:
        image: Input image
        
    Returns:
        Image with normalized lighting
    """
    # Convert to LAB color space
    if len(image.shape) == 3:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        lab = cv2.merge([l, a, b])
        
        # Convert back to BGR
        normalized = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    else:
        # Apply CLAHE to grayscale image
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        normalized = clahe.apply(image)
    
    return normalized


def remove_noise(image):
    """
    Remove noise from image
    
    Args:
        image: Input image
        
    Returns:
        Denoised image
    """
    if len(image.shape) == 3:
        # Color image
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    else:
        # Grayscale image
        denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
    
    return denoised


def validate_image(image, min_size=(48, 48), max_size=(4096, 4096)):
    """
    Validate image dimensions and format
    
    Args:
        image: Input image
        min_size: Minimum allowed size (width, height)
        max_size: Maximum allowed size (width, height)
        
    Returns:
        True if valid, False otherwise
    """
    if image is None:
        return False
    
    if len(image.shape) < 2:
        return False
    
    h, w = image.shape[:2]
    
    if w < min_size[0] or h < min_size[1]:
        return False
    
    if w > max_size[0] or h > max_size[1]:
        return False
    
    return True


def convert_to_pil(image):
    """
    Convert OpenCV image to PIL Image
    
    Args:
        image: OpenCV image (numpy array)
        
    Returns:
        PIL Image
    """
    if len(image.shape) == 2:
        # Grayscale
        return Image.fromarray(image)
    else:
        # Color (convert BGR to RGB)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)


def convert_to_opencv(pil_image):
    """
    Convert PIL Image to OpenCV image
    
    Args:
        pil_image: PIL Image
        
    Returns:
        OpenCV image (numpy array)
    """
    image = np.array(pil_image)
    
    if len(image.shape) == 3:
        # Convert RGB to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    return image

# Made with Bob
