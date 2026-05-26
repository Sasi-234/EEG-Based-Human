# 🚀 SERVER STARTUP GUIDE

## ⚠️ IMPORTANT: Server Not Running

The error "127.0.0.1 refused to connect" means the Django server is not running.

---

## 📋 STEP-BY-STEP STARTUP INSTRUCTIONS

### Step 1: Open PowerShell/Command Prompt

Open a new PowerShell window in your project directory:
```
c:\Users\SadineniSasi\OneDrive - IBM\Desktop\EEG Based Human
```

### Step 2: Check System Status

Run these commands to verify everything is ready:

```powershell
# Check Python version
venv311\Scripts\python.exe --version

# Check if virtual environment works
venv311\Scripts\pip.exe list | findstr "Django opencv pandas"
```

Expected output:
- Python 3.11.x
- Django 4.2.7
- opencv-python (any version)
- pandas (any version)

### Step 3: Run Django Checks

```powershell
cd backend
..\venv311\Scripts\python.exe manage.py check
```

If you see errors, note them down and fix before proceeding.

### Step 4: Run Migrations (IMPORTANT!)

```powershell
# Still in backend directory
..\venv311\Scripts\python.exe manage.py makemigrations
..\venv311\Scripts\python.exe manage.py migrate
```

This creates the database tables for the face_emotion module.

### Step 5: Start the Server

```powershell
# Still in backend directory
..\venv311\Scripts\python.exe manage.py runserver
```

You should see:
```
System check identified no issues (0 silenced).
May 22, 2026 - XX:XX:XX
Django version 4.2.7, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 6: Test the Server

Open your browser and go to:
```
http://127.0.0.1:8000/
```

You should see the home page!

---

## 🔧 TROUBLESHOOTING

### Problem 1: "ModuleNotFoundError: No module named 'cv2'"

**Solution:**
```powershell
venv311\Scripts\pip.exe install opencv-python==4.8.1.78
```

### Problem 2: "numpy.dtype size changed" or NumPy errors

**Solution:**
```powershell
# Uninstall conflicting packages
venv311\Scripts\pip.exe uninstall -y numpy pandas scipy opencv-python

# Install compatible versions
venv311\Scripts\pip.exe install "numpy==1.26.4"
venv311\Scripts\pip.exe install "pandas==2.2.3"
venv311\Scripts\pip.exe install "scipy==1.11.4"
venv311\Scripts\pip.exe install "opencv-python==4.8.1.78"
```

### Problem 3: "TemplateDoesNotExist"

**Solution:** Templates are now created! Just restart the server:
```powershell
# Press CTRL+C to stop server
# Then start again
..\venv311\Scripts\python.exe manage.py runserver
```

### Problem 4: "No migrations to apply"

This is normal if migrations are already applied. Continue to start server.

### Problem 5: Port 8000 already in use

**Solution:**
```powershell
# Use a different port
..\venv311\Scripts\python.exe manage.py runserver 8001
```

Then access at: http://127.0.0.1:8001/

### Problem 6: "RuntimeError: Model class doesn't declare app_label"

**Solution:** Already fixed! The face_emotion app is in INSTALLED_APPS.

---

## ✅ VERIFICATION CHECKLIST

Before starting the server, verify:

- [ ] You're in the project directory
- [ ] Virtual environment (venv311) exists
- [ ] Python 3.11 is installed
- [ ] All dependencies are installed
- [ ] No other server is running on port 8000
- [ ] You're in the `backend` directory when running commands

---

## 🎯 QUICK START (Copy-Paste Commands)

Open PowerShell and run these commands one by one:

```powershell
# Navigate to project
cd "c:\Users\SadineniSasi\OneDrive - IBM\Desktop\EEG Based Human"

# Go to backend
cd backend

# Run migrations
..\venv311\Scripts\python.exe manage.py makemigrations
..\venv311\Scripts\python.exe manage.py migrate

# Start server
..\venv311\Scripts\python.exe manage.py runserver
```

**Keep this terminal open!** The server must stay running.

---

## 🌐 ACCESSING THE APPLICATION

Once the server is running, open your browser and visit:

### Main Pages:
- **Home**: http://127.0.0.1:8000/
- **Login**: http://127.0.0.1:8000/users/login/
- **Register**: http://127.0.0.1:8000/users/register/
- **Dashboard**: http://127.0.0.1:8000/users/dashboard/

### Face Emotion Module:
- **Webcam Capture**: http://127.0.0.1:8000/face-emotion/webcam/
- **Image Upload**: http://127.0.0.1:8000/face-emotion/upload/
- **Prediction History**: http://127.0.0.1:8000/face-emotion/history/
- **Detection Sessions**: http://127.0.0.1:8000/face-emotion/sessions/
- **Real-time Detection**: http://127.0.0.1:8000/face-emotion/realtime/

### EEG Module:
- **EEG Upload**: http://127.0.0.1:8000/eeg/upload/
- **EEG History**: http://127.0.0.1:8000/eeg/history/

### Unified Dashboard:
- **Combined View**: http://127.0.0.1:8000/users/unified-dashboard/

---

## 📝 IMPORTANT NOTES

### 1. Server Must Stay Running
- Don't close the PowerShell window
- The server runs continuously
- Press CTRL+C to stop it

### 2. Login Required
Most pages require you to be logged in:
1. Go to http://127.0.0.1:8000/users/register/
2. Create an account
3. Login
4. Access all features

### 3. Camera Permissions
For webcam features:
- Browser will ask for camera permission
- Click "Allow"
- Use Chrome or Firefox for best results

### 4. File Uploads
For image uploads:
- Supported: JPG, JPEG, PNG, BMP
- Max size: 5MB
- Clear face images work best

---

## 🔄 RESTARTING THE SERVER

If you need to restart:

1. **Stop the server:**
   - Press `CTRL+C` in the terminal

2. **Start again:**
   ```powershell
   ..\venv311\Scripts\python.exe manage.py runserver
   ```

---

## 📊 CHECKING SERVER STATUS

### Server is Running:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Server is NOT Running:
```
Error: That port is already in use.
OR
No output at all
```

---

## 🆘 GETTING HELP

If you encounter errors:

1. **Read the error message** - It usually tells you what's wrong
2. **Check the terminal** - Look for Python errors
3. **Check browser console** - Press F12 in browser
4. **Verify dependencies** - Run `pip list`
5. **Check migrations** - Run `python manage.py showmigrations`

---

## ✅ SUCCESS INDICATORS

You'll know everything is working when:

1. ✅ Server starts without errors
2. ✅ Home page loads at http://127.0.0.1:8000/
3. ✅ You can login/register
4. ✅ Face emotion pages load without "TemplateDoesNotExist"
5. ✅ Webcam works (after granting permissions)
6. ✅ Image upload works
7. ✅ Predictions are displayed

---

## 🎉 READY TO USE!

Once the server is running:
1. Open browser
2. Go to http://127.0.0.1:8000/
3. Register/Login
4. Start using Face Emotion Recognition!

---

**Last Updated**: 2026-05-22  
**Status**: All templates created, server startup required