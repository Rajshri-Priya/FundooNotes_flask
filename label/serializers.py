from pydantic import BaseModel, Field, ConfigDict


class LabelsSerializer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(max_length=150, unique=True)
    color: str = Field(max_length=150)
    user_id: int = None
