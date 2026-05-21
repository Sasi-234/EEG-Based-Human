# EEG-Based Human Emotion Recognition System

A comprehensive web-based AI application that detects human emotions using EEG brainwave signals and deep learning models (CNN and LSTM).

![Project Status](https://img.shields.io/badge/status-planning-blue)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-4.2-green.svg)
![TensorFlow](https://img.shields.io/badge/tensorflow-2.15-orange.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [Emotion Categories](#emotion-categories)
- [Dataset](#dataset)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This system processes EEG signals from the DEAP dataset, applies advanced preprocessing techniques, and uses deep learning models (CNN and LSTM) to classify emotions into six categories: Happy, Sad, Angry, Relaxed, Stressed, and Excited.

### Key Applications
- 🏥 Healthcare and mental health monitoring
- 🧠 Human-computer interaction
- 📊 Emotion analysis and research
- 💡 Personalized recommendations

---

## ✨ Features

### User Features
- ✅ User registration and authentication
- 📤 EEG data upload (CSV, DAT formats)
- 🔍 Real-time emotion prediction
- 📈 Emotion history and analytics
- 📊 Interactive visualization dashboard
- 📄 Downloadable emotion reports
- 💡 Personalized recommendations

### Admin Features
- 👥 User management
- 📁 File management
- 📊 System analytics
- 🎯 Model performance monitoring
- 📝 Activity logs

### Technical Features
- 🧠 CNN and LSTM deep learning models
- 🔧 Advanced EEG signal preprocessing
- 🚀 Real-time prediction API
- 📱 Responsive web interface
- 🔒 Secure authentication
- 📊 Data visualization with Chart.js

---

## 🛠️ Technology Stack

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- Bootstrap 5
- Chart.js for visualization
- jQuery

### Backend
- Python 3.8+
- Django 4.2
- Django REST Framework
- SQLite (development) / PostgreSQL (production)

### AI/ML
- TensorFlow 2.15
- Keras
- NumPy, Pandas
- Scikit-learn
- MNE-Python (EEG processing)
- SciPy

### Development Tools
- Git
- Docker
- Jupyter Notebook
- pytest

---

## 📁 Project Structure

```
eeg-emotion-recognition/
├── backend/
│   ├── config/              # Django project settings
│   ├── users/               # User management app
│   ├── eeg_processing/      # EEG data processing
│   ├── ml_models/           # Deep learning models
│   ├── api/                 # REST API endpoints
│   ├── recommendations/     # Recommendation engine
│   ├── media/               # Uploaded files
│   ├── static/              # Static assets
│   └── templates/           # HTML templates
├── dataset/
│   └── DEAP/                # DEAP dataset
├── notebooks/               # Jupyter notebooks
├── tests/                   # Test files
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
├── PROJECT_PLAN.md          # Detailed project plan
├── TECHNICAL_SPECIFICATIONS.md  # Technical specs
├── IMPLEMENTATION_GUIDE.md  # Implementation guide
└── README.md                # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd eeg-emotion-recognition
```

2. **Create virtual environment**
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up Django**
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

5. **Run development server**
```bash
python manage.py runserver
```

6. **Access the application**
- Frontend: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- API: http://localhost:8000/api

---

## 📚 Documentation

Comprehensive documentation is available in the following files:

- **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Complete project architecture, phases, and roadmap
- **[TECHNICAL_SPECIFICATIONS.md](TECHNICAL_SPECIFICATIONS.md)** - Detailed technical specifications
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Step-by-step implementation guide

### Quick Links
- [System Architecture](PROJECT_PLAN.md#system-architecture)
- [Database Schema](PROJECT_PLAN.md#database-schema)
- [API Documentation](TECHNICAL_SPECIFICATIONS.md#api-endpoint-specifications)
- [Model Architecture](TECHNICAL_SPECIFICATIONS.md#cnn-model-architecture-details)
- [Setup Guide](IMPLEMENTATION_GUIDE.md#phase-1-environment-setup)

---

## 😊 Emotion Categories

The system classifies EEG signals into six emotion categories:

| Emotion | Valence | Arousal | Description |
|---------|---------|---------|-------------|
| **Happy** | High (6-9) | High (6-9) | Positive, energetic state |
| **Excited** | High (6-9) | Very High (7-9) | Highly positive, very energetic |
| **Relaxed** | High (6-9) | Low (1-4) | Positive, calm state |
| **Sad** | Low (1-4) | Low (1-4) | Negative, low energy |
| **Angry** | Low (1-4) | High (6-9) | Negative, high energy |
| **Stressed** | Low-Mid (1-5) | High (6-9) | Negative, tense state |

---

## 📊 Dataset

### DEAP Dataset
- **Name**: Database for Emotion Analysis using Physiological signals
- **Participants**: 32 subjects
- **Trials**: 40 music video trials per participant
- **Duration**: 60 seconds per trial
- **Channels**: 32 EEG channels
- **Sampling Rate**: 128 Hz (downsampled from 512 Hz)

### Data Format
- **Input**: EEG signals (32 channels × time points)
- **Labels**: Valence, Arousal, Dominance, Liking (1-9 scale)
- **Supported Formats**: CSV, DAT, EDF, BDF

### Download Dataset
The DEAP dataset can be obtained from:
- Official Website: https://www.eecs.qmul.ac.uk/mmv/datasets/deap/

---

## 🔧 Development Workflow

### Phase 1: Setup (Week 1)
- ✅ Environment setup
- ✅ Django project initialization
- ✅ Database configuration

### Phase 2: Backend (Weeks 2-4)
- Database models
- User authentication
- EEG processing pipeline
- API endpoints

### Phase 3: ML Models (Weeks 4-6)
- CNN model implementation
- LSTM model implementation
- Model training and evaluation

### Phase 4: Frontend (Weeks 7-9)
- UI/UX design
- Template creation
- Dashboard implementation
- Visualization components

### Phase 5: Integration (Week 10)
- Frontend-backend integration
- Testing
- Bug fixes

### Phase 6: Deployment (Week 11)
- Production setup
- Docker configuration
- Deployment

---

## 🧪 Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_models.py
```

---

## 📈 Performance Metrics

### Target Metrics
- **Model Accuracy**: >85% for both CNN and LSTM
- **Prediction Time**: <5 seconds per file
- **API Response Time**: <500ms
- **System Uptime**: >99%

---

## 🔒 Security

- Password hashing using PBKDF2
- CSRF protection
- XSS prevention
- SQL injection prevention
- Secure file upload validation
- Rate limiting on API endpoints

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Team

- **Project Type**: Academic/Research Project
- **Domain**: AI/ML, Healthcare, Neuroscience
- **Status**: In Development

---

## 📞 Support

For questions or support:
- Create an issue in the repository
- Check the documentation files
- Review the implementation guide

---

## 🎯 Roadmap

### Current Phase: Planning ✅
- [x] Project architecture design
- [x] Technical specifications
- [x] Implementation guide
- [x] Documentation

### Next Phase: Implementation
- [ ] Django setup
- [ ] Database models
- [ ] EEG preprocessing
- [ ] ML model development
- [ ] Frontend development
- [ ] Testing
- [ ] Deployment

---

## 🌟 Acknowledgments

- DEAP Dataset creators
- TensorFlow and Keras teams
- Django community
- MNE-Python developers

---

## 📊 Project Statistics

- **Lines of Code**: TBD
- **Test Coverage**: TBD
- **Documentation**: Comprehensive
- **Models**: CNN + LSTM
- **Emotions Detected**: 6 categories

---

**Last Updated**: 2026-05-21  
**Version**: 1.0.0  
**Status**: Planning Phase Complete ✅

---

Made with ❤️ for advancing emotion recognition technology