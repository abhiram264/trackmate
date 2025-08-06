from pydantic import BaseModel, EmailStr

class StudentRegistryCreate(BaseModel):
    student_id: str
    email: EmailStr
    full_name: str
    college_name:str
    department:str

class StudentRegistryRead(StudentRegistryCreate):
    id: int
    
    class Config:
        orm_mode = True

