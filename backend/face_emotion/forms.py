from django import forms
from django.core.validators import FileExtensionValidator
from PIL import Image
from .models import FaceEmotionPrediction


class FaceImageUploadForm(forms.ModelForm):
    """
    Form for uploading face images for emotion detection
    """
    class Meta:
        model = FaceEmotionPrediction
        fields = ['image', 'notes']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/bmp',
                'id': 'imageUpload',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this image...',
            }),
        }
        labels = {
            'image': 'Select Face Image',
            'notes': 'Notes (Optional)',
        }
        help_texts = {
            'image': 'Upload a clear image containing a face (JPG, PNG, or BMP format)',
        }
    
    def clean_image(self):
        """Validate uploaded image"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file size must be less than 5MB.')
            
            # Check file extension
            valid_extensions = ['jpg', 'jpeg', 'png', 'bmp']
            ext = image.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Invalid file extension. Allowed: {", ".join(valid_extensions)}'
                )
        
        return image


class WebcamCaptureForm(forms.Form):
    """
    Form for capturing images from webcam
    """
    captured_image = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
        help_text='Base64 encoded image data from webcam'
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes about this capture...',
        }),
        required=False,
        label='Notes (Optional)'
    )
    
    def clean_captured_image(self):
        """Validate base64 image data"""
        image_data = self.cleaned_data.get('captured_image')
        
        if image_data:
            # Check if it's valid base64 data
            if not image_data.startswith('data:image'):
                raise forms.ValidationError('Invalid image data format.')
            
            # Extract base64 part
            try:
                header, encoded = image_data.split(',', 1)
                if len(encoded) < 100:  # Too small to be a valid image
                    raise forms.ValidationError('Image data is too small.')
            except ValueError:
                raise forms.ValidationError('Invalid image data structure.')
        
        return image_data


class FaceEmotionFilterForm(forms.Form):
    """
    Form for filtering face emotion predictions
    """
    EMOTION_CHOICES = [
        ('', 'All Emotions'),
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('fear', 'Fear'),
        ('neutral', 'Neutral'),
        ('surprise', 'Surprise'),
        ('stress', 'Stress'),
        ('relaxed', 'Relaxed'),
    ]
    
    METHOD_CHOICES = [
        ('', 'All Methods'),
        ('webcam', 'Webcam'),
        ('upload', 'Upload'),
        ('realtime', 'Real-time'),
    ]
    
    emotion = forms.ChoiceField(
        choices=EMOTION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Filter by Emotion'
    )
    
    method = forms.ChoiceField(
        choices=METHOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Filter by Method'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='From Date'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='To Date'
    )
    
    min_confidence = forms.FloatField(
        required=False,
        min_value=0.0,
        max_value=1.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00 - 1.00',
        }),
        label='Minimum Confidence'
    )


class SessionNotesForm(forms.Form):
    """
    Form for adding notes to detection sessions
    """
    session_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Add notes about this detection session...',
        }),
        required=True,
        label='Session Notes',
        max_length=1000
    )


class BulkImageUploadForm(forms.Form):
    """
    Form for uploading an image file
    """
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/jpg,image/png,image/bmp',
        }),
        required=True,
        label='Select Image',
        help_text='Upload a single image file (JPG, PNG, BMP)',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp'])]
    )
    
    def clean_image(self):
        """Validate image upload"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image is too large. Maximum size is 5MB.')
            
            # Validate it's a real image
            try:
                img = Image.open(image)
                img.verify()
            except Exception:
                raise forms.ValidationError('Invalid image file.')
        
        return image

# Made with Bob
