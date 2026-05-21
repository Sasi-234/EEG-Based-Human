"""
Unit tests for Django models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from eeg_processing.models import EEGUpload, EmotionPrediction, PreprocessingLog
from ml_models.models import ModelVersion, ModelTrainingLog, ModelEvaluationMetrics
from recommendations.models import Recommendation, RecommendationTemplate, UserRecommendationFeedback
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_str(self):
        """Test user string representation"""
        self.assertEqual(str(self.user), 'testuser')


class EEGUploadModelTest(TestCase):
    """Test EEGUpload model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a simple uploaded file
        self.test_file = SimpleUploadedFile(
            "test_eeg.csv",
            b"test content",
            content_type="text/csv"
        )
    
    def test_eeg_upload_creation(self):
        """Test EEG upload is created correctly"""
        upload = EEGUpload.objects.create(
            user=self.user,
            file_path=self.test_file,
            file_name='test_eeg.csv',
            file_size=1024,
            status='pending'
        )
        
        self.assertEqual(upload.user, self.user)
        self.assertEqual(upload.file_name, 'test_eeg.csv')
        self.assertEqual(upload.status, 'pending')
    
    def test_eeg_upload_str(self):
        """Test EEG upload string representation"""
        upload = EEGUpload.objects.create(
            user=self.user,
            file_path=self.test_file,
            file_name='test_eeg.csv'
        )
        self.assertIn('test_eeg.csv', str(upload))


class EmotionPredictionModelTest(TestCase):
    """Test EmotionPrediction model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.test_file = SimpleUploadedFile(
            "test_eeg.csv",
            b"test content",
            content_type="text/csv"
        )
        
        self.upload = EEGUpload.objects.create(
            user=self.user,
            file_path=self.test_file,
            file_name='test_eeg.csv'
        )
    
    def test_emotion_prediction_creation(self):
        """Test emotion prediction is created correctly"""
        prediction = EmotionPrediction.objects.create(
            user=self.user,
            upload=self.upload,
            predicted_emotion='happy',
            confidence_score=95.5,
            valence=80.0,
            arousal=70.0
        )
        
        self.assertEqual(prediction.predicted_emotion, 'happy')
        self.assertEqual(prediction.confidence_score, 95.5)
        self.assertEqual(prediction.valence, 80.0)
    
    def test_emotion_choices(self):
        """Test emotion choices are valid"""
        valid_emotions = ['happy', 'sad', 'angry', 'relaxed', 'excited', 'stressed']
        
        for emotion in valid_emotions:
            prediction = EmotionPrediction.objects.create(
                user=self.user,
                upload=self.upload,
                predicted_emotion=emotion,
                confidence_score=90.0
            )
            self.assertEqual(prediction.predicted_emotion, emotion)


class ModelVersionTest(TestCase):
    """Test ModelVersion model"""
    
    def test_model_version_creation(self):
        """Test model version is created correctly"""
        model_version = ModelVersion.objects.create(
            model_name='CNN_Emotion_Classifier',
            model_type='cnn',
            version='1.0.0',
            accuracy=0.92,
            status='active'
        )
        
        self.assertEqual(model_version.model_type, 'cnn')
        self.assertEqual(model_version.version, '1.0.0')
        self.assertEqual(model_version.accuracy, 0.92)
        self.assertTrue(model_version.is_active)


class RecommendationModelTest(TestCase):
    """Test Recommendation model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.test_file = SimpleUploadedFile(
            "test_eeg.csv",
            b"test content",
            content_type="text/csv"
        )
        
        self.upload = EEGUpload.objects.create(
            user=self.user,
            file_path=self.test_file,
            file_name='test_eeg.csv'
        )
        
        self.prediction = EmotionPrediction.objects.create(
            user=self.user,
            upload=self.upload,
            predicted_emotion='stressed',
            confidence_score=88.0
        )
    
    def test_recommendation_creation(self):
        """Test recommendation is created correctly"""
        recommendation = Recommendation.objects.create(
            user=self.user,
            prediction=self.prediction,
            recommendation_type='meditation',
            title='Try Deep Breathing',
            description='Practice deep breathing for 5 minutes',
            priority=1
        )
        
        self.assertEqual(recommendation.recommendation_type, 'meditation')
        self.assertEqual(recommendation.priority, 1)
        self.assertTrue(recommendation.is_active)
    
    def test_recommendation_mark_as_viewed(self):
        """Test marking recommendation as viewed"""
        recommendation = Recommendation.objects.create(
            user=self.user,
            prediction=self.prediction,
            recommendation_type='activity',
            title='Go for a walk'
        )
        
        self.assertIsNone(recommendation.viewed_at)
        recommendation.mark_as_viewed()
        self.assertIsNotNone(recommendation.viewed_at)


class RecommendationTemplateTest(TestCase):
    """Test RecommendationTemplate model"""
    
    def test_template_creation(self):
        """Test recommendation template is created correctly"""
        template = RecommendationTemplate.objects.create(
            emotion='happy',
            recommendation_type='activity',
            title='Share Your Joy',
            description='Connect with friends and share your positive energy',
            priority=1
        )
        
        self.assertEqual(template.emotion, 'happy')
        self.assertTrue(template.is_active)

# Made with Bob
