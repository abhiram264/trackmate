# TrackMate - AI-Powered Lost & Found System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![SQLModel](https://img.shields.io/badge/SQLModel-Latest-red.svg)](https://sqlmodel.tiangolo.com)

A comprehensive lost and found tracking system designed for university campuses with JWT authentication and RESTful API.

## 🚀 Features Implemented

- **🔐 JWT Authentication**: Secure token-based authentication with student registry verification
- **📦 Lost Items Management**: Create, search, and manage lost item reports
- **🔍 Found Items Management**: Submit and track found items
- **⚖️ Claims System**: Structured claim process for item recovery
- **🖼️ Image Upload System**: Support for item image uploads
- **📚 Auto-Generated API Docs**: Interactive Swagger UI documentation
- **🔒 Security**: Password hashing, JWT tokens, input validation

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite with SQLModel ORM
- **Authentication**: JWT with bcrypt password hashing
- **Validation**: Pydantic v2 schemas
- **Documentation**: Automatic OpenAPI/Swagger generation
- **File Upload**: Multi-part form data support

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (for cloning)

## ⚡ Quick Start

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/trackmate.git
cd trackmate

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env
# Default settings work out of the box for development!
```

### 3. Initialize Database

```bash
# Create database tables and add test data
python init_db.py
```

Expected output:
```
🔧 Creating database tables...
✅ Test student data created successfully!
📧 Test emails available:
   - john.doe@university.edu (ID: STU001)
   - jane.smith@university.edu (ID: STU002)
   - admin@university.edu (ID: STU003)
```

### 4. Start the Server

```bash
# Start development server
uvicorn app.main:app --reload
```

Server will be available at:
- 🌐 **Main API**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs
- 📖 **Alternative Docs**: http://localhost:8000/redoc

## 🧪 Testing the API

### Step 1: Access API Documentation

Open http://localhost:8000/docs in your browser to see the interactive Swagger UI.

### Step 2: Test Authentication (✅ TESTED)

#### A. User Registration
1. **Endpoint**: `POST /api/v1/auth/signup`
2. **Click**: "Try it out"
3. **Request Body**:
```json
{
  "email": "john.doe@university.edu",
  "password": "password123",
  "student_id": "STU001",
  "full_name": "John Doe"
}
```
4. **Expected Result**: ✅ `201 Created` with user details

#### B. User Login
1. **Endpoint**: `POST /api/v1/auth/login`
2. **Request Body**:
```json
{
  "email": "john.doe@university.edu",
  "password": "password123"
}
```
3. **Expected Result**: ✅ `200 OK` with JWT tokens
4. **⚠️ Important**: Copy the `access_token` for next steps

#### C. Authorization Setup
1. **Click**: 🔒 **"Authorize"** button at top of Swagger UI
2. **Enter**: `Bearer YOUR_ACCESS_TOKEN_HERE` (include "Bearer " prefix)
3. **Click**: "Authorize" then "Close"
4. **Verify**: Lock icon shows closed 🔒

#### D. Get Current User Profile
1. **Endpoint**: `GET /api/v1/auth/me`
2. **Expected Result**: ✅ `200 OK` with your user information

#### E. Update User Profile (✅ TESTED - FIXED)
1. **Endpoint**: `PUT /api/v1/auth/profile`
2. **Request Body**:
```json
{
  "phone": "123-456-7890",
  "bio": "Test user for TrackMate API"
}
```
3. **Expected Result**: ✅ `200 OK` with updated profile
4. **Note**: Fixed - User model now includes phone and bio fields

### Step 3: Test Core Endpoints (Ready for Testing)

#### 📦 Lost Items Management
**Create Lost Item**: `POST /api/v1/lost-items/`
```json
{
  "title": "Lost iPhone 13",
  "description": "Black iPhone 13 Pro with cracked screen protector",
  "category": "electronics",
  "location_lost": "Library 2nd Floor",
  "date_lost": "2025-08-06T14:30:00",
  "contact_info": "john.doe@university.edu",
  "reward_offered": "$50"
}
```

**Other Endpoints Available**:
- `GET /api/v1/lost-items/` - List all items
- `GET /api/v1/lost-items/{id}` - Get specific item
- `PUT /api/v1/lost-items/{id}` - Update item
- `GET /api/v1/lost-items/my-items/` - Your items only

#### 🔍 Found Items Management  
**Create Found Item**: `POST /api/v1/found-items/`
```json
{
  "title": "Found Samsung Galaxy",
  "description": "Samsung Galaxy S21 in blue case",
  "category": "electronics",
  "location_found": "Cafeteria",
  "date_found": "2025-08-06T16:00:00",
  "current_location": "Security Office",
  "handover_instructions": "Contact security 9-5 PM"
}
```

#### ⚖️ Claims System
**Create Claim**: `POST /api/v1/claims/`
```json
{
  "found_item_id": 1,
  "claim_reason": "This is my Samsung Galaxy. Lost it yesterday in cafeteria.",
  "contact_info": "john.doe@university.edu, 123-456-7890"
}
```

#### 🖼️ Image Upload
**Upload Image**: `POST /api/v1/images/upload`
- **Parameters**: 
  - `file`: Select image file (.jpg, .png, .webp)
  - `item_id`: ID of lost/found item
  - `item_type`: "lost" or "found"

## 📊 Current System Status

### ✅ Completed & Working
- [x] JWT Authentication system
- [x] User registration with student verification
- [x] User login and token generation
- [x] Protected endpoints with authorization
- [x] User profile management
- [x] Database initialization with test data
- [x] API documentation generation
- [x] Error handling and validation

### 🔧 Ready for Testing
- [ ] Lost items CRUD operations
- [ ] Found items CRUD operations
- [ ] Claims management system
- [ ] Image upload functionality
- [ ] Search and filtering
- [ ] Admin approval workflows

### 📝 Test Accounts Available
| Email | Student ID | Password | Purpose |
|-------|------------|----------|---------|
| john.doe@university.edu | STU001 | Any password | Regular user testing |
| jane.smith@university.edu | STU002 | Any password | Multi-user testing |
| admin@university.edu | STU003 | Any password | Admin features |

## 🔧 Configuration

### Environment Variables (.env)
```env
DATABASE_URL=sqlite:///./trackmate.db
SECRET_KEY=TrackMate_SuperSecure_Key_2025_Change_This_In_Production_xyz789abc123def456
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=true
ENVIRONMENT=development
```

### Item Categories Available
- `electronics` - Phones, laptops, headphones
- `clothing` - Jackets, bags, shoes  
- `accessories` - Jewelry, watches, glasses
- `books` - Textbooks, notebooks
- `documents` - IDs, certificates
- `sports` - Equipment, uniforms
- `bags` - Backpacks, purses
- `jewelry` - Rings, necklaces
- `keys` - Room keys, car keys
- `others` - Miscellaneous items

## 🔍 Troubleshooting

### Common Issues

**ModuleNotFoundError:**
```bash
# Run from project root directory
cd C:\Users\ramab\trackmate
python init_db.py
```

**Database Issues:**
```bash
# Reset database if needed
del trackmate.db  # Windows
rm trackmate.db   # Mac/Linux
python init_db.py
```

**Server Won't Start:**
```bash
# Check if port 8000 is free
uvicorn app.main:app --reload --port 8001
```

**Import Errors:**
```bash
# Set Python path
set PYTHONPATH=%PYTHONPATH%;C:\Users\ramab\trackmate
uvicorn app.main:app --reload
```

## 🗂️ Project Structure

```
trackmate/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependencies
│   │   └── v1/              # API version 1
│   │       ├── __init__.py
│   │       ├── auth.py      # ✅ Authentication endpoints
│   │       ├── lost_items.py
│   │       ├── found_items.py
│   │       ├── claims.py
│   │       └── images.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # ✅ App configuration
│   │   └── security.py      # ✅ JWT & password utils
│   ├── models/              # ✅ Database models
│   │   ├── __init__.py
│   │   ├── user.py          # ✅ Fixed with phone/bio fields
│   │   ├── student_registry.py
│   │   ├── lost_item.py
│   │   ├── found_item.py
│   │   ├── claim.py
│   │   └── image_model.py
│   └── schemas/             # ✅ Pydantic schemas
│       ├── __init__.py
│       ├── user.py
│       ├── lost_item.py
│       ├── found_item.py
│       ├── claim.py
│       └── base_schema.py
├── .env                     # ✅ Environment variables
├── .env.example             # ✅ Environment template
├── .gitignore              # ✅ Git ignore rules
├── init_db.py              # ✅ Database initialization
├── requirements.txt        # ✅ Dependencies
└── README.md               # ✅ This file
```

## 🚀 Next Testing Steps

1. **Test Lost Items Management**
   - Create, read, update, delete lost items
   - Test search and filtering functionality

2. **Test Found Items Management**  
   - Submit found items
   - Test availability tracking

3. **Test Claims System**
   - Create claims for found items
   - Test admin approval workflow

4. **Test Image Upload**
   - Upload images for items
   - Verify file handling and storage

5. **Test Edge Cases**
   - Invalid data validation
   - Unauthorized access attempts
   - Non-existent resource requests

## 📄 License

This project is licensed under the MIT License.

---

**Current Status**: Authentication system fully tested ✅ | Core endpoints ready for testing 🧪

For support or issues, please check the troubleshooting section above.
