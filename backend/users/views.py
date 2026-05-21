from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, PasswordChangeCustomForm
from .models import User, UserActivityLog
from eeg_processing.models import EEGUpload, EmotionPrediction
from django.db.models import Count
from datetime import datetime, timedelta


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(user, activity_type, description, request):
    """Helper function to log user activity"""
    UserActivityLog.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
    )


def home(request):
    """Home page view"""
    context = {
        'total_users': User.objects.count(),
        'total_predictions': EmotionPrediction.objects.count(),
        'total_uploads': EEGUpload.objects.count(),
    }
    return render(request, 'home.html', context)


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the registration
            log_activity(user, 'login', 'User registered successfully', request)
            # Log the user in
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            # Try to authenticate with username
            user = authenticate(username=username, password=password)
            
            # If authentication failed, try with email
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is not None:
                login(request, user)
                
                # Set session expiry
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires when browser closes
                
                # Log the login
                log_activity(user, 'login', 'User logged in', request)
                
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next page or dashboard
                next_page = request.GET.get('next', 'dashboard')
                return redirect(next_page)
            else:
                messages.error(request, 'Invalid username/email or password.')
        else:
            messages.error(request, 'Invalid username/email or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def user_logout(request):
    """User logout view"""
    # Log the logout
    log_activity(request.user, 'logout', 'User logged out', request)
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    """User dashboard view"""
    user = request.user
    
    # Get user statistics
    total_uploads = EEGUpload.objects.filter(user=user).count()
    total_predictions = EmotionPrediction.objects.filter(user=user).count()
    
    # Get recent uploads
    recent_uploads = EEGUpload.objects.filter(user=user).order_by('-upload_date')[:5]
    
    # Get recent predictions
    recent_predictions = EmotionPrediction.objects.filter(user=user).order_by('-prediction_date')[:5]
    
    # Get emotion distribution
    emotion_distribution = EmotionPrediction.objects.filter(user=user).values('predicted_emotion').annotate(
        count=Count('predicted_emotion')
    ).order_by('-count')
    
    # Get recent activity
    recent_activity = UserActivityLog.objects.filter(user=user).order_by('-timestamp')[:10]
    
    context = {
        'total_uploads': total_uploads,
        'total_predictions': total_predictions,
        'recent_uploads': recent_uploads,
        'recent_predictions': recent_predictions,
        'emotion_distribution': emotion_distribution,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'profile_update', 'User updated profile', request)
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})


@login_required
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            log_activity(request.user, 'password_change', 'User changed password', request)
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeCustomForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


@login_required
def activity_log(request):
    """View user activity log"""
    activities = UserActivityLog.objects.filter(user=request.user).order_by('-timestamp')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(activities, 20)  # Show 20 activities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/activity_log.html', {'page_obj': page_obj})


def about(request):
    """About page view"""
    return render(request, 'about.html')

# Made with Bob
