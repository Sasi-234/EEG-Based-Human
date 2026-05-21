# How to Run the EEG Emotion Recognition System

## ⚠️ Important: Python Version Requirement

**Current Issue**: You are using Python 3.14, but TensorFlow (required for the deep learning models) only supports Python 3.10-3.12.

## 🔧 Solution Options

### Option 1: Install Python 3.11 (Recommended)

1. **Download Python 3.11**
   - Visit: https://www.python.org/downloads/
   - Download Python 3.11.x (latest stable)
   - Install with "Add to PATH" checked

2. **Create New Virtual Environment**
   ```bash
   # Create virtual environment with Python 3.11
   py -3.11 -m venv venv311
   
   # Activate it
   venv311\Scripts\activate
   
   # Install all dependencies
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

4. **Access the Application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

---

### Option 2: Run Without TensorFlow (Limited Functionality)

You can run the system without the ML models to see the interface and basic functionality:

1. **Wait for Current Installation to Complete**
   The pip install command is still running. Wait for it to finish.

2. **Comment Out TensorFlow Imports**
   I'll create a version that works without TensorFlow.

3. **Run Basic Version**
   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

---

## 📋 What You Can Test Without TensorFlow

✅ **Working Features:**
- User registration and login
- User dashboard
- EEG file upload interface
- File management (view, delete uploads)
- Admin interface
- Database operations
- Frontend templates
- API endpoints (structure)

❌ **Not Working Without TensorFlow:**
- Actual emotion prediction
- Model training
- CNN/LSTM models
- Signal preprocessing (requires SciPy)

---

## 🚀 Quick Demo Steps (After Installation)

### 1. Start the Server
```bash
cd backend
python manage.py runserver
```

### 2. Create Admin User
```bash
python manage.py createsuperuser
# Enter username, email, password
```

### 3. Access the System

**Main Application:**
- Home: http://localhost:8000
- Register: http://localhost:8000/users/register/
- Login: http://localhost:8000/users/login/
- Dashboard: http://localhost:8000/users/dashboard/
- Upload EEG: http://localhost:8000/eeg/upload/

**Admin Panel:**
- Admin: http://localhost:8000/admin
- Login with superuser credentials

### 4. Test the Features

1. **Register a new user**
   - Go to http://localhost:8000/users/register/
   - Fill in the form
   - Submit

2. **Login**
   - Use your credentials
   - Access dashboard

3. **Upload EEG File**
   - Go to upload page
   - Select a .csv file (create a test file if needed)
   - Upload

4. **View Admin Panel**
   - Login to admin
   - See all models
   - Manage data

---

## 📊 Expected Results

### Home Page
- Welcome message
- Feature cards
- Statistics
- Navigation menu

### Dashboard
- User statistics
- Recent uploads
- Quick actions
- Charts (using Chart.js)

### Upload Page
- File upload form
- Recent uploads list
- Status indicators
- File validation

### Admin Panel
- User management
- Upload monitoring
- Prediction logs
- Model versions
- Customized interface with badges

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'numpy'"
**Solution**: Wait for pip installation to complete, or install manually:
```bash
pip install numpy pandas scipy scikit-learn matplotlib pillow djangorestframework
```

### Issue: "ModuleNotFoundError: No module named 'tensorflow'"
**Solution**: 
- Use Python 3.10-3.12
- Install TensorFlow: `pip install tensorflow`

### Issue: "No such table" errors
**Solution**: Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: Port 8000 already in use
**Solution**: Use different port:
```bash
python manage.py runserver 8080
```

---

## 📸 Screenshots to Expect

### 1. Home Page
- Clean, modern interface
- Bootstrap 5 styling
- Feature cards
- Emotion badges

### 2. Login Page
- Simple login form
- Remember me checkbox
- Register link

### 3. Dashboard
- Statistics cards
- Recent activity
- Charts
- Quick actions

### 4. Upload Page
- Drag-and-drop area
- File requirements
- Recent uploads
- Status badges

### 5. Admin Panel
- Django admin interface
- Custom styling
- Color-coded badges
- Data tables

---

## 🎯 Next Steps After Running

1. **Test User Registration**
2. **Test File Upload**
3. **Explore Admin Panel**
4. **Check Database**
5. **Test API Endpoints** (using Postman or curl)
6. **Review Logs**

---

## 📞 Need Help?

If you encounter issues:
1. Check the terminal output for errors
2. Review the error messages
3. Check if all dependencies are installed
4. Verify Python version
5. Ensure database migrations are run

---

## ✅ Success Indicators

You'll know it's working when you see:
- ✅ Server starts without errors
- ✅ Home page loads at http://localhost:8000
- ✅ Can register and login
- ✅ Dashboard displays correctly
- ✅ Can upload files
- ✅ Admin panel is accessible

---

**Current Status**: Waiting for dependency installation to complete.
**Recommended Action**: Install Python 3.11 for full functionality.