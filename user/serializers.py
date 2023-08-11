from pydantic import BaseModel, Field, EmailStr


class RegistrationSerializer(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=3, max_length=15)  # Minimum length of 4 characters
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: int
    location: str = Field(min_length=3, max_length=100)


class LoginSerializer(BaseModel):
    username: str = Field(min_length=3, max_length=50,
                          pattern=r"^[a-zA-Z0-9_-]+$")  # Alphanumeric, underscores, and hyphens allowed
    password: str = Field(min_length=3, max_length=15)  # Minimum length of 4 characters
