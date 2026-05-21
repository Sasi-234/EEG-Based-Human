from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import EEGUpload
import os


class EEGUploadForm(forms.ModelForm):
    """
    Form for uploading EEG files
    """
    class Meta:
        model = EEGUpload
        fields = ['file_path', 'description']
        widgets = {
            'file_path': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.csv,.dat,.edf,.bdf'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description of the EEG data...'
            }),
        }
        labels = {
            'file_path': 'EEG File',
            'description': 'Description (Optional)'
        }
    
    def clean_file_path(self):
        """Validate uploaded file"""
        file = self.cleaned_data.get('file_path')
        
        if not file:
            raise ValidationError("Please select a file to upload.")
        
        # Check file extension
        ext = os.path.splitext(file.name)[1].lower()
        allowed_extensions = getattr(settings, 'ALLOWED_EXTENSIONS', ['.csv', '.dat', '.edf', '.bdf'])
        
        if ext not in allowed_extensions:
            raise ValidationError(
                f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Check file size
        max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 52428800)  # 50MB default
        if file.size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise ValidationError(
                f"File size exceeds maximum allowed size of {max_size_mb:.0f}MB."
            )
        
        return file
    
    def save(self, commit=True):
        """Save the upload with additional information"""
        instance = super().save(commit=False)
        
        # Set file name and size
        if instance.file_path:
            instance.file_name = instance.file_path.name
            instance.file_size = instance.file_path.size
        
        if commit:
            instance.save()
        
        return instance

# Made with Bob
