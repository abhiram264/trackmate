 
# TrackMate - AI-Powered Lost & Found System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![SQLModel](https://img.shields.io/badge/SQLModel-Latest-red.svg)](https://sqlmodel.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive lost and found tracking system designed for university campuses, powered by AI image matching and natural language processing.

## 🚀 Features

- **🔐 JWT Authentication**: Secure token-based authentication with student registry verification
- **📦 Lost Items Management**: Create, search, update, and manage lost item reports
- **🔍 Found Items Management**: Submit and track found items with detailed information
- **⚖️ Claims System**: Structured claim process with admin approval workflow
- **🖼️ Image Upload**: Support for multiple image uploads per item
- **🔎 Advanced Search**: Filter by category, location, date, status, and keywords
- **👨‍💼 Admin Dashboard**: Comprehensive admin tools for managing claims and items
- **📚 Auto-Generated Docs**: Complete OpenAPI/Swagger documentation
- **🔒 Security**: Password hashing, JWT tokens, input validation

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Authentication**: JWT with bcrypt password hashing
- **Validation**: Pydantic v2 with comprehensive schemas
- **Documentation**: Automatic OpenAPI/Swagger generation
- **File Upload**: Multi-part form data with image validation
- **CORS**: Cross-origin resource sharing enabled

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (for cloning)
- A web browser (for testing via Swagger UI)

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

# Edit .env file with your settings (optional for development)
# Default settings work out of the box!
```

### 3. Initialize Database

```bash
# Create database tables and add test data
python init_db.py
```

You should see:
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

# Server will be available at:
# 🌐 http://localhost:8000
# 📚 API Docs: http://localhost:8000/docs
# 📖 ReDoc: http://localhost:8000/redoc
```

## 🧪 API Testing Guide

### Step 1: Access API Documentation

Open your browser and go to: **http://localhost:8000/docs**

You'll see the interactive Swagger UI with all available endpoints organized by categories:
- 🔐 **Authentication** (6 endpoints)
- 📦 **Lost Items** (8 endpoints) 
- 🔍 **Found Items** (8 endpoints)
- ⚖️ **Claims** (7 endpoints)
- 🖼️ **Images** (4 endpoints)

### Step 2: Test Authentication Flow

#### A. User Registration
1. **Find**: `POST /api/v1/auth/signup`
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
4. **Click**: "Execute"
5. **Expected**: `201 Created` with user details

#### B. User Login
1. **Find**: `POST /api/v1/auth/login`
2. **Request Body**:
```json
{
  "email": "john.doe@university.edu",
  "password": "password123"
}
```
3. **Execute** and **copy the `access_token`** from response

#### C. Authorize for Protected Endpoints
1. **Click**: 🔒 **"Authorize"** button at top of page
2. **Enter**: `Bearer YOUR_ACCESS_TOKEN_HERE`
3. **Click**: "Authorize" then "Close"
4. **Verify**: Lock icon changes to closed 🔒

### Step 3: Test Core Functionality

#### 📦 Lost Items Management

**Create Lost Item:**
```json
{
  "title": "Lost iPhone 13 Pro",
  "description": "Black iPhone 13 Pro with cracked screen protector, found near library",
  "category": "electronics",
  "location_lost": "Main Library 2nd Floor",
  "date_lost": "2025-08-06T14:30:00",
  "contact_info": "john.doe@university.edu",
  "reward_offered": "$50 reward"
}
```

**Test Endpoints:**
- `GET /api/v1/lost-items/` - List all items (with pagination)
- `GET /api/v1/lost-items/{id}` - Get specific item
- `PUT /api/v1/lost-items/{id}` - Update item
- `GET /api/v1/lost-items/my-items/` - Your items only
- `PATCH /api/v1/lost-items/{id}/status?new_status=claimed` - Update status

#### 🔍 Found Items Management

**Create Found Item:**
```json
{
  "title": "Found Samsung Galaxy S21",
  "description": "Samsung Galaxy S21 in blue protective case, found in cafeteria",
  "category": "electronics", 
  "location_found": "Student Cafeteria",
  "date_found": "2025-08-06T12:00:00",
  "current_location": "Campus Security Office",
  "handover_instructions": "Contact security between 9 AM - 5 PM, bring student ID"
}
```

**Test Endpoints:**
- `GET /api/v1/found-items/available/` - Only available items
- `PUT /api/v1/found-items/{id}` - Update found item
- `GET /api/v1/found-items/my-items/` - Items you found

#### ⚖️ Claims System

**Create Claim:**
```json
{
  "found_item_id": 1,
  "claim_reason": "This is my Samsung Galaxy S21. I lost it yesterday in the cafeteria around lunch time. The blue case has my initials 'JD' written on the back in permanent marker.",
  "contact_info": "john.doe@university.edu, Phone: (555) 123-4567"
}
```

**Admin Actions** (requires admin user):
- `GET /api/v1/claims/pending/` - Pending claims
- `PUT /api/v1/claims/{id}/approve` - Approve claim
- `PUT /api/v1/claims/{id}/reject` - Reject with reason

#### 🖼️ Image Upload

**Upload Image:**
1. **Endpoint**: `POST /api/v1/images/upload`
2. **Parameters**:
   - `file`: Select a .jpg/.png image file
   - `item_id`: ID of your lost/found item
   - `item_type`: "lost" or "found"
3. **Execute**

### Step 4: Advanced Testing

#### Search & Filtering

Test search functionality with query parameters:

**Lost Items Search:**
```
GET /api/v1/lost-items/?search=iPhone&category=electronics&status=active&page=1&limit=10
```

**Filter Parameters:**
- `search`: Keyword search in title/description
- `category`: electronics, clothing, books, etc.
- `status`: active, claimed, resolved, expired
- `location`: Location-based filtering
- `date_from` / `date_to`: Date range filtering
- `page` / `limit`: Pagination

#### Error Testing

Test error handling:
1. **401 Unauthorized**: Try protected endpoints without authorization
2. **404 Not Found**: Request non-existent item `GET /api/v1/lost-items/99999`
3. **422 Validation Error**: Send invalid data (empty required fields)
4. **403 Forbidden**: Try admin endpoints with regular user

## 📊 Test Data Overview

The system includes pre-configured test data:

### Test Student Accounts
| Email | Student ID | Department | Use Case |
|-------|------------|------------|----------|
| john.doe@university.edu | STU001 | Computer Science | Regular user testing |
| jane.smith@university.edu | STU002 | Information Technology | Multi-user testing |
| admin@university.edu | STU003 | Administration | Admin functionality |

### Item Categories
- `electronics` - Phones, laptops, headphones
- `clothing` - Jackets, bags, shoes
- `accessories` - Jewelry, watches, glasses
- `books` - Textbooks, notebooks
- `documents` - IDs, certificates, papers
- `sports` - Equipment, uniforms
- `bags` - Backpacks, purses, briefcases
- `jewelry` - Rings, necklaces, bracelets
- `keys` - Room keys, car keys, keychains
- `others` - Miscellaneous items

### Item Statuses
- `active` - Currently lost/found and available
- `claimed` - Claim submitted but not resolved
- `resolved` - Successfully returned to owner
- `expired` - No longer actively tracked

## 🔧 Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=sqlite:///./trackmate.db

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload
UPLOAD_DIRECTORY=uploaded_images
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.webp

# Application
DEBUG=true
ENVIRONMENT=development
```

### Database Schema

The system uses 6 main tables:
- **users** - User accounts and authentication
- **student_registry** - Valid student database
- **lost_items** - Lost item reports
- **found_items** - Found item submissions  
- **claims** - Item claim requests
- **images** - File uploads linked to items

## 📈 API Endpoint Summary

| Category | Endpoints | Description |
|----------|-----------|-------------|
| Authentication | 6 | Signup, login, profile, tokens |
| Lost Items | 8 | CRUD operations, search, status updates |
| Found Items | 8 | CRUD operations, availability tracking |
| Claims | 7 | Create, approve, reject, track claims |
| Images | 4 | Upload, retrieve, item associations |
| **Total** | **33** | **Comprehensive REST API** |

## 🔍 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn app.main:app --reload
```

**Database Issues:**
```bash
# Reset database
rm trackmate.db
python init_db.py
```

**Permission Errors:**
```bash
# Check file permissions
ls -la trackmate.db
chmod 664 trackmate.db
```

**Port Already in Use:**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Debug Mode

Enable detailed logging:
```bash
# Set debug in .env
DEBUG=true

# Or run with debug logging
uvicorn app.main:app --reload --log-level debug
```

## 🚀 Production Deployment

### Environment Setup
```env
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=very-long-random-secret-key
DATABASE_URL=postgresql://user:pass@localhost/trackmate
ALLOWED_ORIGINS=https://yourdomain.com
```

### Security Checklist
- ✅ Change default `SECRET_KEY`
- ✅ Use PostgreSQL in production
- ✅ Set strong passwords
- ✅ Configure CORS origins
- ✅ Enable HTTPS
- ✅ Set up proper logging
- ✅ Configure file upload limits

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test thoroughly
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Development Workflow
```bash
# Setup development environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run tests
pytest

# Start development server
uvicorn app.main:app --reload

# Check code style
black app/
flake8 app/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases with Python
- [Pydantic](https://docs.pydantic.dev/) - Data validation using Python type hints
- [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server

## 📞 Support

If you encounter any issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review API documentation at `/docs`
3. Check server logs for error details
4. Verify your environment configuration
5. Ensure test data is properly initialized

## 🏆 Project Status

- ✅ **Core API**: Complete with 33 endpoints
- ✅ **Authentication**: JWT-based security system
- ✅ **Database**: Full schema with relationships
- ✅ **Documentation**: Auto-generated OpenAPI docs
- ✅ **File Upload**: Image handling system
- ✅ **Admin Tools**: Claim management system
- 🚧 **AI Integration**: Planned for future releases
- 🚧 **Frontend**: Separate React/Vue.js application planned

---

**Happy Testing! 🧪✨**

For questions or support, please open an issue on GitHub.
