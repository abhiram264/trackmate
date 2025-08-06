"""
Database initialization script for TrackMate
Run this once to create tables and add test data
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.database import init_db, get_db
from app.models.student_registry import StudentRegistry
from sqlalchemy.orm import Session

def create_test_data():
    """Create test student data for development"""
    
    # Initialize database tables
    print("🔧 Creating database tables...")
    init_db()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if test data already exists
        existing_student = db.query(StudentRegistry).filter(
            StudentRegistry.email == "john.doe@university.edu"
        ).first()
        
        if existing_student:
            print("✅ Test data already exists!")
            return
        
        # Create test students for development
        test_students = [
            StudentRegistry(
                student_id="STU001",
                email="john.doe@university.edu",
                full_name="John Doe",
                college_name="Test University",
                department="Computer Science"
            ),
            StudentRegistry(
                student_id="STU002", 
                email="jane.smith@university.edu",
                full_name="Jane Smith",
                college_name="Test University",
                department="Information Technology"
            ),
            StudentRegistry(
                student_id="STU003",
                email="admin@university.edu", 
                full_name="Admin User",
                college_name="Test University",
                department="Administration"
            )
        ]
        
        # Add test students to database
        for student in test_students:
            db.add(student)
        
        db.commit()
        print("✅ Test student data created successfully!")
        print("📧 Test emails available:")
        for student in test_students:
            print(f"   - {student.email} (ID: {student.student_id})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
