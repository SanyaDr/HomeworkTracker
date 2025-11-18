from pydantic import BaseModel

class User(BaseModel):
    login: str
    email: str | None = None
    name: str | None = None
    groupName: str | None = None
    is_active: bool
    created_at: str
    
