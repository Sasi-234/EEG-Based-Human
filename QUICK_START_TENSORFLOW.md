# 🚀 Quick Start Guide - TensorFlow Setup

## ✅ Automated Setup (RECOMMENDED)

I've created an automated setup script for you!

### **Option 1: Run the Setup Script**

1. **Open Command Prompt** (not PowerShell)
2. **Navigate to your project:**
   ```bash
   cd "C:\Users\SadineniSasi\OneDrive - IBM\Desktop\EEG Based Human"
   ```
3. **Run the setup script:**
   ```bash
   setup_python311.bat
   ```

The script will automatically:
- ✅ Install Python 3.11 (if needed)
- ✅ Create virtual environment
- ✅ Install TensorFlow and all dependencies
- ✅ Run database migrations
- ✅ Prepare the system for predictions

**Total time: 10-15 minutes**

---

## 📋 Manual Setup (Alternative)

If the automated script doesn't work, follow these steps:

### **Step 1: Wait for Python 3.11 Installation**

The installation is currently running in Terminal 2. Wait for it to complete (2-5 minutes).

### **Step 2: Verify Installation**

Open a **NEW** Command Prompt and run:
```bash
py -3.11 --version
```

Expected output: `Python 3.11.9`

### **Step 3: Create Virtual Environment**

```bash
cd "C:\Users\SadineniSasi\OneDrive - IBM\Desktop\EEG Based Human"
py -3.11 -m venv venv311
```

### **Step 4: Activate Virtual Environment**

```bash
venv311\Scripts\activate.bat
```

You should see `(venv311)` at the start of your prompt.

### **Step 5: Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Django 4.2.7
- TensorFlow 2.15.0
- Keras 2.15.0
- NumPy, Pandas, SciPy
- Scikit-learn, Matplotlib
- MNE (EEG processing)
- All other dependencies

**Installation time: 5-10 minutes**

### **Step 6: Run Migrations**

```bash
cd backend
python manage.py migrate
```

### **Step 7: Start Server**

```bash
python manage.py runserver
```

Server will start at: **http://127.0.0.1:8000/**

---

## 🎯 After Setup - Testing Predictions

### **1. Upload Your CSV File**

Go to: http://127.0.0.1:8000/eeg/upload/

Upload your 19-channel CSV file:
- Channels: Fp1, Fp2, F3, F4, F7, F8, T3, T4, C3, C4, T5, T6, P3, P4, O1, O2, Fz, Cz, Pz
- Format: CSV
- Max size: 100 MB

### **2. Wait for Processing**

Processing time: **30-60 seconds**

The system will:
1. Read your CSV file
2. Preprocess signals (filtering, normalization)
3. Extract features
4. Run CNN/LSTM model
5. Predict emotion

### **3. View Results**

Results will show:
- **Emotion**: Happy, Sad, Angry, Relaxed, Stressed, or Excited
- **Confidence**: 0-100%
- **Valence**: Positive/Negative emotion scale
- **Arousal**: Energy level
- **Recommendations**: Personalized suggestions

### **4. View All Predictions**

Go to: http://127.0.0.1:8000/eeg/predictions/

See all your emotion predictions with:
- Emotion badges
- Confidence scores
- Timestamps
- Filter by emotion

---

## 🔧 Troubleshooting

### **Issue: Python 3.11 not found**

Try:
```bash
py install 3.11
```

Or download manually from: https://www.python.org/downloads/release/python-3119/

### **Issue: Virtual environment activation fails**

For PowerShell, run first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate:
```powershell
venv311\Scripts\Activate.ps1
```

### **Issue: TensorFlow installation fails**

Make sure you're using Python 3.11 (not 3.14):
```bash
python --version
```

Should show: `Python 3.11.9`

### **Issue: Predictions not working**

Check if TensorFlow is installed:
```bash
python -c "import tensorflow as tf; print(tf.__version__)"
```

Should show: `2.15.0` or similar

---

## 📊 System Requirements

### **Minimum:**
- Python 3.11
- 4 GB RAM
- 2 GB free disk space
- Windows 10/11

### **Recommended:**
- Python 3.11
- 8 GB RAM
- 5 GB free disk space
- GPU (optional, for faster processing)

---

## ⏰ Processing Times

| File Size | Processing Time |
|-----------|----------------|
| < 1 MB    | 15-30 seconds  |
| 1-10 MB   | 30-90 seconds  |
| 10-50 MB  | 2-5 minutes    |
| 50-100 MB | 5-10 minutes   |

---

## 🎉 What You'll Get

After setup, your system will have:

✅ **User Features:**
- Register and login
- Upload EEG CSV files
- Get emotion predictions
- View prediction history
- Download reports
- Personalized recommendations

✅ **Admin Features:**
- User management
- Upload monitoring
- Prediction logs
- System analytics
- Model performance tracking

✅ **AI Features:**
- CNN emotion recognition
- LSTM emotion recognition
- 6 emotion classes
- Confidence scoring
- Valence/Arousal metrics
- Feature extraction

---

## 📞 Need Help?

If you encounter any issues:

1. Check Terminal 2 for Python 3.11 installation status
2. Make sure virtual environment is activated (you see `(venv311)`)
3. Verify TensorFlow is installed: `pip list | findstr tensorflow`
4. Check server logs for errors

---

## 🚀 Quick Commands Reference

```bash
# Navigate to project
cd "C:\Users\SadineniSasi\OneDrive - IBM\Desktop\EEG Based Human"

# Activate virtual environment
venv311\Scripts\activate.bat

# Start server
cd backend
python manage.py runserver

# Check TensorFlow
python -c "import tensorflow as tf; print(tf.__version__)"

# View installed packages
pip list
```

---

**Your EEG Emotion Recognition System is almost ready!** 🎊

Just run the setup script and you'll be predicting emotions in 15 minutes!