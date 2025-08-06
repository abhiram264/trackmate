from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class StudentRegistry(SQLModel, table = True):
    __tablename__ = "student_registry"

    id: Optional[int] = Field(default = None, primary_key = True)
    student_id: str = Field(index = True,nullable = False)
    email: str = Field(index = True,nullable = False,unique = True)
    full_name :str = Field(nullable = False)
    college_name :str = Field(nullable = False)
    department: str = Field(nullable = False)

    academic_year: Optional[str] = Field(default=None)
    graduation_year: Optional[int] = Field(default=None)

    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
