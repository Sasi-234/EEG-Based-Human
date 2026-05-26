"""
Real-time Face Detection and Emotion Recognition using OpenCV
Standalone script that can be run independently or integrated with Django
"""

import cv2
import numpy as np
import time
import os
import sys
from datetime import datetime
from collections import deque

# Add parent directory to path for Django imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class RealtimeFaceEmotionDetector:
    """
    Real-time face detection and emotion recognition using webcam
    """
    
    def __init__(self, camera_index=0, use_django=False):
        """
        Initialize the real-time detector
        
        Args:
            camera_index: Camera device index (0 for default webcam)
            use_django: Whether to use Django models for saving predictions
        """
        self.camera_index = camera_index
        self.use_django = use_django
        self.cap = None
        self.face_cascade = None
        self.emotion_model = None
        self.is_running = False
        
        # Statistics
        self.frame_count = 0
        self.face_count = 0
        self.fps = 0
        self.emotion_history = deque(maxlen=30)  # Last 30 emotions
        
        # Emotion labels and colors
        self.emotions = ['angry', 'fear', 'happy', 'neutral', 'relaxed', 'sad', 'stress', 'surprise']
        self.emotion_colors = {
            'happy': (0, 215, 255),      # Gold
            'sad': (255, 105, 65),       # Royal Blue
            'angry': (60, 20, 220),      # Crimson
            'fear': (219, 112, 147),     # Medium Purple
            'neutral': (128, 128, 128),  # Gray
            'surprise': (180, 105, 255), # Hot Pink
            'stress': (0, 69, 255),      # Orange Red
            'relaxed': (50, 205, 50),    # Lime Green
        }
        
        # Initialize components
        self._load_face_cascade()
        if use_django:
            self._load_emotion_model()
    
    def _load_face_cascade(self):
        """Load Haar Cascade for face detection"""
        try:
            # Try OpenCV's built-in cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                raise Exception("Failed to load Haar Cascade")
            
            print("✓ Face cascade loaded successfully")
            
        except Exception as e:
            print(f"✗ Error loading face cascade: {e}")
            # Try alternative path
            alt_path = os.path.join(
                os.path.dirname(__file__),
                'saved_models',
                'haarcascade_frontalface_default.xml'
            )
            if os.path.exists(alt_path):
                self.face_cascade = cv2.CascadeClassifier(alt_path)
                print("✓ Face cascade loaded from alternative path")
            else:
                print("✗ Face cascade not found. Face detection will not work.")
    
    def _load_emotion_model(self):
        """Load emotion recognition model (Django integration)"""
        try:
            # Import Django components
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
            import django
            django.setup()
            
            from face_emotion.emotion_model import load_pretrained_model
            
            self.emotion_model = load_pretrained_model()
            print("✓ Emotion model loaded successfully")
            
        except Exception as e:
            print(f"✗ Error loading emotion model: {e}")
            print("  Running in face detection only mode")
    
    def start_camera(self):
        """Initialize and start the camera"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                raise Exception(f"Cannot open camera {self.camera_index}")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"✓ Camera {self.camera_index} opened successfully")
            print(f"  Resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            print(f"  FPS: {int(self.cap.get(cv2.CAP_PROP_FPS))}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error starting camera: {e}")
            return False
    
    def stop_camera(self):
        """Release the camera"""
        if self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
            print("✓ Camera released")
    
    def detect_faces(self, frame):
        """
        Detect faces in a frame
        
        Args:
            frame: Input frame (BGR image)
            
        Returns:
            List of face bounding boxes [(x, y, w, h), ...]
        """
        if self.face_cascade is None:
            return []
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces
    
    def predict_emotion(self, face_image):
        """
        Predict emotion from face image
        
        Args:
            face_image: Grayscale face image (48x48)
            
        Returns:
            Dictionary with emotion and confidence
        """
        if self.emotion_model is None:
            return {'emotion': 'neutral', 'confidence': 0.0}
        
        try:
            # Preprocess face
            face_resized = cv2.resize(face_image, (48, 48))
            face_normalized = face_resized.astype('float32') / 255.0
            face_input = np.expand_dims(face_normalized, axis=-1)
            face_input = np.expand_dims(face_input, axis=0)
            
            # Predict
            result = self.emotion_model.predict(face_input)
            
            return result
            
        except Exception as e:
            print(f"Error predicting emotion: {e}")
            return {'emotion': 'neutral', 'confidence': 0.0}
    
    def draw_face_box(self, frame, x, y, w, h, emotion=None, confidence=None):
        """
        Draw bounding box around face with emotion label
        
        Args:
            frame: Input frame
            x, y, w, h: Face bounding box coordinates
            emotion: Detected emotion (optional)
            confidence: Confidence score (optional)
        """
        # Get color for emotion
        color = self.emotion_colors.get(emotion, (0, 255, 0)) if emotion else (0, 255, 0)
        
        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        # Draw label if emotion is provided
        if emotion:
            label = f"{emotion.upper()}"
            if confidence:
                label += f" {confidence*100:.1f}%"
            
            # Calculate label size
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            
            # Draw label background
            cv2.rectangle(
                frame,
                (x, y - label_h - 10),
                (x + label_w, y),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                frame,
                label,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
    
    def draw_statistics(self, frame):
        """
        Draw statistics overlay on frame
        
        Args:
            frame: Input frame
        """
        height, width = frame.shape[:2]
        
        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw statistics text
        stats = [
            f"FPS: {self.fps:.1f}",
            f"Frames: {self.frame_count}",
            f"Faces Detected: {self.face_count}",
            f"Detection Rate: {(self.face_count/max(self.frame_count,1)*100):.1f}%"
        ]
        
        y_offset = 35
        for stat in stats:
            cv2.putText(
                frame,
                stat,
                (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
            y_offset += 25
    
    def draw_emotion_history(self, frame):
        """
        Draw emotion history graph
        
        Args:
            frame: Input frame
        """
        if len(self.emotion_history) < 2:
            return
        
        height, width = frame.shape[:2]
        
        # Create graph area
        graph_x = width - 310
        graph_y = 10
        graph_w = 300
        graph_h = 150
        
        # Draw background
        overlay = frame.copy()
        cv2.rectangle(overlay, (graph_x, graph_y), (graph_x + graph_w, graph_y + graph_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw title
        cv2.putText(
            frame,
            "Emotion Timeline",
            (graph_x + 10, graph_y + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )
        
        # Count emotions
        emotion_counts = {}
        for emotion in self.emotion_history:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Draw bars
        if emotion_counts:
            max_count = max(emotion_counts.values())
            y_pos = graph_y + 50
            
            for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                bar_width = int((count / max_count) * (graph_w - 100))
                color = self.emotion_colors.get(emotion, (128, 128, 128))
                
                # Draw bar
                cv2.rectangle(
                    frame,
                    (graph_x + 80, y_pos),
                    (graph_x + 80 + bar_width, y_pos + 15),
                    color,
                    -1
                )
                
                # Draw label
                cv2.putText(
                    frame,
                    f"{emotion[:6]}",
                    (graph_x + 10, y_pos + 12),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 255, 255),
                    1
                )
                
                # Draw count
                cv2.putText(
                    frame,
                    str(count),
                    (graph_x + 85 + bar_width, y_pos + 12),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 255, 255),
                    1
                )
                
                y_pos += 20
    
    def process_frame(self, frame):
        """
        Process a single frame: detect faces and predict emotions
        
        Args:
            frame: Input frame
            
        Returns:
            Processed frame with annotations
        """
        # Detect faces
        faces = self.detect_faces(frame)
        
        # Process each face
        for (x, y, w, h) in faces:
            self.face_count += 1
            
            # Extract face region
            face_gray = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY)
            
            # Predict emotion if model is available
            if self.emotion_model is not None:
                result = self.predict_emotion(face_gray)
                emotion = result['emotion']
                confidence = result['confidence']
                
                # Add to history
                self.emotion_history.append(emotion)
                
                # Draw face box with emotion
                self.draw_face_box(frame, x, y, w, h, emotion, confidence)
            else:
                # Draw face box without emotion
                self.draw_face_box(frame, x, y, w, h)
        
        return frame
    
    def run(self, show_stats=True, show_history=True, save_video=False):
        """
        Run real-time face detection and emotion recognition
        
        Args:
            show_stats: Show statistics overlay
            show_history: Show emotion history graph
            save_video: Save output video to file
        """
        if not self.start_camera():
            return
        
        self.is_running = True
        
        # Video writer for saving
        video_writer = None
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'face_emotion_output_{timestamp}.avi'
            video_writer = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
            print(f"✓ Saving video to: {output_path}")
        
        print("\n" + "="*60)
        print("Real-time Face Emotion Detection Started")
        print("="*60)
        print("Controls:")
        print("  SPACE - Capture screenshot")
        print("  S     - Toggle statistics")
        print("  H     - Toggle history graph")
        print("  R     - Reset statistics")
        print("  Q/ESC - Quit")
        print("="*60 + "\n")
        
        # FPS calculation
        fps_start_time = time.time()
        fps_frame_count = 0
        
        try:
            while self.is_running:
                # Read frame
                ret, frame = self.cap.read()
                
                if not ret:
                    print("✗ Failed to read frame")
                    break
                
                # Flip frame horizontally (mirror effect)
                frame = cv2.flip(frame, 1)
                
                # Process frame
                frame = self.process_frame(frame)
                
                # Draw overlays
                if show_stats:
                    self.draw_statistics(frame)
                
                if show_history:
                    self.draw_emotion_history(frame)
                
                # Calculate FPS
                fps_frame_count += 1
                if fps_frame_count >= 10:
                    fps_end_time = time.time()
                    self.fps = fps_frame_count / (fps_end_time - fps_start_time)
                    fps_start_time = fps_end_time
                    fps_frame_count = 0
                
                # Update frame count
                self.frame_count += 1
                
                # Save frame if recording
                if video_writer is not None:
                    video_writer.write(frame)
                
                # Display frame
                cv2.imshow('Face Emotion Detection', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # Q or ESC
                    break
                elif key == ord(' '):  # SPACE - Screenshot
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f'screenshot_{timestamp}.jpg'
                    cv2.imwrite(filename, frame)
                    print(f"✓ Screenshot saved: {filename}")
                elif key == ord('s'):  # S - Toggle stats
                    show_stats = not show_stats
                    print(f"Statistics: {'ON' if show_stats else 'OFF'}")
                elif key == ord('h'):  # H - Toggle history
                    show_history = not show_history
                    print(f"History: {'ON' if show_history else 'OFF'}")
                elif key == ord('r'):  # R - Reset stats
                    self.frame_count = 0
                    self.face_count = 0
                    self.emotion_history.clear()
                    print("✓ Statistics reset")
        
        except KeyboardInterrupt:
            print("\n✓ Interrupted by user")
        
        finally:
            # Cleanup
            if video_writer is not None:
                video_writer.release()
                print(f"✓ Video saved")
            
            self.stop_camera()
            
            # Print final statistics
            print("\n" + "="*60)
            print("Session Statistics")
            print("="*60)
            print(f"Total Frames: {self.frame_count}")
            print(f"Faces Detected: {self.face_count}")
            print(f"Detection Rate: {(self.face_count/max(self.frame_count,1)*100):.1f}%")
            print(f"Average FPS: {self.fps:.1f}")
            
            if self.emotion_history:
                print("\nEmotion Distribution:")
                emotion_counts = {}
                for emotion in self.emotion_history:
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                
                for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / len(self.emotion_history)) * 100
                    print(f"  {emotion.capitalize():10s}: {count:3d} ({percentage:5.1f}%)")
            
            print("="*60 + "\n")


def main():
    """Main function to run the detector"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time Face Emotion Detection')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    parser.add_argument('--django', action='store_true', help='Use Django integration for emotion prediction')
    parser.add_argument('--no-stats', action='store_true', help='Hide statistics overlay')
    parser.add_argument('--no-history', action='store_true', help='Hide emotion history graph')
    parser.add_argument('--save', action='store_true', help='Save output video')
    
    args = parser.parse_args()
    
    # Create detector
    detector = RealtimeFaceEmotionDetector(
        camera_index=args.camera,
        use_django=args.django
    )
    
    # Run detector
    detector.run(
        show_stats=not args.no_stats,
        show_history=not args.no_history,
        save_video=args.save
    )


if __name__ == '__main__':
    main()

# Made with Bob
