from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import EEGUpload, EmotionPrediction
from .forms import EEGUploadForm
from users.models import UserActivityLog
import os


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(user, activity_type, description, request):
    """Log user activity"""
    UserActivityLog.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
    )


@login_required
def upload_eeg(request):
    """View for uploading EEG files"""
    if request.method == 'POST':
        form = EEGUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            upload.status = 'pending'
            upload.save()
            
            # Log the upload
            log_activity(
                request.user,
                'upload',
                f'Uploaded EEG file: {upload.file_name}',
                request
            )
            
            messages.success(
                request,
                f'File "{upload.file_name}" uploaded successfully! Processing will begin shortly.'
            )
            return redirect('eeg_upload_detail', upload_id=upload.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EEGUploadForm()
    
    # Get recent uploads
    recent_uploads = EEGUpload.objects.filter(user=request.user).order_by('-upload_date')[:5]
    
    context = {
        'form': form,
        'recent_uploads': recent_uploads,
    }
    return render(request, 'eeg/upload.html', context)


@login_required
def eeg_upload_list(request):
    """View for listing all EEG uploads"""
    uploads = EEGUpload.objects.filter(user=request.user).order_by('-upload_date')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        uploads = uploads.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(uploads, 10)  # Show 10 uploads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'eeg/upload_list.html', context)


@login_required
def eeg_upload_detail(request, upload_id):
    """View for displaying EEG upload details"""
    upload = get_object_or_404(EEGUpload, id=upload_id, user=request.user)
    
    # Get predictions for this upload
    predictions = EmotionPrediction.objects.filter(upload=upload).order_by('-prediction_date')
    
    context = {
        'upload': upload,
        'predictions': predictions,
    }
    return render(request, 'eeg/upload_detail.html', context)


@login_required
def eeg_upload_delete(request, upload_id):
    """View for deleting an EEG upload"""
    upload = get_object_or_404(EEGUpload, id=upload_id, user=request.user)
    
    if request.method == 'POST':
        file_name = upload.file_name
        upload.delete()
        
        # Log the deletion
        log_activity(
            request.user,
            'upload',
            f'Deleted EEG file: {file_name}',
            request
        )
        
        messages.success(request, f'File "{file_name}" has been deleted successfully.')
        return redirect('eeg_upload_list')
    
    context = {'upload': upload}
    return render(request, 'eeg/upload_confirm_delete.html', context)


@login_required
def prediction_list(request):
    """View for listing all emotion predictions"""
    predictions = EmotionPrediction.objects.filter(user=request.user).order_by('-prediction_date')
    
    # Filter by emotion if provided
    emotion_filter = request.GET.get('emotion')
    if emotion_filter:
        predictions = predictions.filter(predicted_emotion=emotion_filter)
    
    # Pagination
    paginator = Paginator(predictions, 15)  # Show 15 predictions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'emotion_filter': emotion_filter,
        'emotion_choices': EmotionPrediction.EMOTION_CHOICES,
    }
    return render(request, 'eeg/prediction_list.html', context)


@login_required
def prediction_detail(request, prediction_id):
    """View for displaying prediction details"""
    prediction = get_object_or_404(EmotionPrediction, id=prediction_id, user=request.user)
    
    context = {
        'prediction': prediction,
    }
    return render(request, 'eeg/prediction_detail.html', context)

# Made with Bob
