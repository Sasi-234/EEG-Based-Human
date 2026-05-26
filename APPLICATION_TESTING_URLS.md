# Complete Application Testing URLs

## How to Test
1. Start the Django server:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. Open your browser and test each URL below
3. Check the boxes as you test each URL

---

## 🏠 PUBLIC PAGES (No Login Required)

### ✅ Home & About
- [ ] **Home Page**
  - URL: `http://127.0.0.1:8000/`
  - Should show: Welcome page with statistics and features
  - Test: Click "Get Started" button

- [ ] **About Page**
  - URL: `http://127.0.0.1:8000/about/`
  - Should show: Information about the project

---

## 👤 USER AUTHENTICATION PAGES

### ✅ Registration & Login
- [ ] **User Registration**
  - URL: `http://127.0.0.1:8000/users/register/`
  - Test: Create a new account
  - Should redirect to dashboard after successful registration

- [ ] **User Login**
  - URL: `http://127.0.0.1:8000/users/login/`
  - Test: Login with your credentials
  - Should redirect to dashboard after successful login

- [ ] **User Logout**
  - URL: `http://127.0.0.1:8000/users/logout/`
  - Test: Click logout from navigation menu
  - Should redirect to home page

---

## 📊 USER DASHBOARD (Login Required)

### ✅ Main Dashboard
- [ ] **User Dashboard**
  - URL: `http://127.0.0.1:8000/users/dashboard/`
  - Should show: Statistics, recent uploads, recent predictions
  - Test: Click "Edit Profile" button

- [ ] **User Profile**
  - URL: `http://127.0.0.1:8000/users/profile/`
  - Should show: User information form
  - Test: Update profile information

- [ ] **Activity Log**
  - URL: `http://127.0.0.1:8000/users/activity-log/`
  - Should show: List of user activities with timestamps

---

## 🧠 EEG EMOTION RECOGNITION (Login Required)

### ✅ EEG Upload & Processing
- [ ] **EEG File Upload**
  - URL: `http://127.0.0.1:8000/eeg/upload/`
  - Should show: File upload form
  - Test: Upload a sample EEG file (.csv, .dat, .edf, .bdf)

- [ ] **EEG Upload List**
  - URL: `http://127.0.0.1:8000/eeg/uploads/`
  - Should show: List of all uploaded EEG files
  - Test: Click on an upload to view details

- [ ] **EEG Upload Detail**
  - URL: `http://127.0.0.1:8000/eeg/upload/<id>/`
  - Replace `<id>` with actual upload ID (e.g., 1)
  - Example: `http://127.0.0.1:8000/eeg/upload/1/`
  - Should show: Upload details, preprocessing status, predictions

- [ ] **EEG Prediction List**
  - URL: `http://127.0.0.1:8000/eeg/predictions/`
  - Should show: List of all emotion predictions
  - Test: Filter by emotion, date, model

- [ ] **EEG Prediction Detail**
  - URL: `http://127.0.0.1:8000/eeg/prediction/<id>/`
  - Replace `<id>` with actual prediction ID
  - Example: `http://127.0.0.1:8000/eeg/prediction/1/`
  - Should show: Detailed prediction results with charts

---

## 😊 FACE EMOTION RECOGNITION (Login Required)

### ✅ Face Emotion Detection
- [ ] **Image Upload**
  - URL: `http://127.0.0.1:8000/face-emotion/upload/`
  - Should show: Image upload form
  - Test: Upload a face image (.jpg, .png)

- [ ] **Webcam Capture**
  - URL: `http://127.0.0.1:8000/face-emotion/webcam/`
  - Should show: Webcam interface
  - Test: Allow camera access and capture image

- [ ] **Real-time Detection**
  - URL: `http://127.0.0.1:8000/face-emotion/realtime/`
  - Should show: Live webcam feed with emotion detection
  - Test: Allow camera access and see real-time emotion labels

- [ ] **Prediction History**
  - URL: `http://127.0.0.1:8000/face-emotion/history/`
  - Should show: List of face emotion predictions
  - Test: Filter by emotion, date, confidence

- [ ] **Prediction Detail**
  - URL: `http://127.0.0.1:8000/face-emotion/prediction/<id>/`
  - Replace `<id>` with actual prediction ID
  - Example: `http://127.0.0.1:8000/face-emotion/prediction/1/`
  - Should show: Detailed prediction with image and confidence scores

- [ ] **Detection Sessions**
  - URL: `http://127.0.0.1:8000/face-emotion/sessions/`
  - Should show: List of real-time detection sessions

- [ ] **Session Detail**
  - URL: `http://127.0.0.1:8000/face-emotion/session/<id>/`
  - Replace `<id>` with actual session ID
  - Example: `http://127.0.0.1:8000/face-emotion/session/1/`
  - Should show: Session details with emotion timeline

---

## 💡 RECOMMENDATIONS (Login Required)

### ✅ Emotion-Based Recommendations
- [ ] **Recommendations Dashboard**
  - URL: `http://127.0.0.1:8000/recommendations/`
  - Should show: Personalized recommendations based on emotions

- [ ] **Recommendation History**
  - URL: `http://127.0.0.1:8000/recommendations/history/`
  - Should show: Past recommendations

---

## 🔧 ADMIN PANEL (Admin Login Required)

### ✅ Django Admin
- [ ] **Admin Login**
  - URL: `http://127.0.0.1:8000/admin/`
  - Test: Login with superuser credentials
  - Should show: Django admin dashboard

- [ ] **User Management**
  - URL: `http://127.0.0.1:8000/admin/users/user/`
  - Should show: List of all users

- [ ] **EEG Uploads Management**
  - URL: `http://127.0.0.1:8000/admin/eeg_processing/eegupload/`
  - Should show: List of all EEG uploads

- [ ] **Predictions Management**
  - URL: `http://127.0.0.1:8000/admin/eeg_processing/emotionprediction/`
  - Should show: List of all predictions

- [ ] **Face Emotion Management**
  - URL: `http://127.0.0.1:8000/admin/face_emotion/faceemotionprediction/`
  - Should show: List of face emotion predictions

---

## 🔗 API ENDPOINTS (For Testing with Postman/curl)

### ✅ REST API
- [ ] **API Root**
  - URL: `http://127.0.0.1:8000/api/`
  - Should show: Available API endpoints

- [ ] **EEG Upload API**
  - URL: `http://127.0.0.1:8000/api/eeg/upload/`
  - Method: POST
  - Test: Upload EEG file via API

- [ ] **Prediction API**
  - URL: `http://127.0.0.1:8000/api/eeg/predict/`
  - Method: POST
  - Test: Get emotion prediction via API

- [ ] **Face Emotion API**
  - URL: `http://127.0.0.1:8000/api/face-emotion/predict/`
  - Method: POST
  - Test: Upload face image and get emotion via API

---

## 📱 NAVIGATION MENU LINKS

Test all navigation menu links by clicking them:

### When NOT Logged In:
- [ ] Home
- [ ] About
- [ ] Login
- [ ] Register

### When Logged In:
- [ ] Home
- [ ] Dashboard
- [ ] EEG Upload
- [ ] Face Emotion
- [ ] Profile
- [ ] Activity Log
- [ ] Logout

---

## 🎯 QUICK TEST WORKFLOW

### 1. First Time Setup
```bash
# Create superuser (if not created)
cd backend
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### 2. Basic Flow Test
1. Visit home page → Click "Get Started"
2. Register new account
3. Login with credentials
4. View dashboard
5. Upload EEG file (if you have sample data)
6. Upload face image or use webcam
7. View predictions
8. Check recommendations
9. Update profile
10. Logout

### 3. Admin Test
1. Go to `/admin/`
2. Login with superuser
3. Check all models are visible
4. View uploaded data
5. Check predictions

---

## ⚠️ Common Issues & Solutions

### Issue 1: NoReverseMatch Error
**Solution:** Check if URL namespace is correct (users:, face_emotion:, etc.)

### Issue 2: 404 Page Not Found
**Solution:** Verify URL pattern in urls.py files

### Issue 3: Permission Denied
**Solution:** Make sure you're logged in for protected pages

### Issue 4: Static Files Not Loading
**Solution:** Run `python manage.py collectstatic`

### Issue 5: Database Error
**Solution:** Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📊 Testing Checklist Summary

- [ ] All public pages load (2 pages)
- [ ] User authentication works (3 pages)
- [ ] User dashboard accessible (3 pages)
- [ ] EEG processing works (5 pages)
- [ ] Face emotion detection works (7 pages)
- [ ] Recommendations accessible (2 pages)
- [ ] Admin panel accessible (5 sections)
- [ ] Navigation menu works (all links)
- [ ] API endpoints respond (4 endpoints)

**Total URLs to Test: 30+**

---

## 🎉 Success Criteria

✅ All pages load without errors  
✅ Navigation works smoothly  
✅ User can register and login  
✅ File uploads work  
✅ Predictions are generated  
✅ Admin panel accessible  
✅ No NoReverseMatch errors  
✅ No 404 errors on valid URLs

---

**Last Updated:** 2026-05-22  
**Status:** Ready for comprehensive testing