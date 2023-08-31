from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Annotated
from pydantic.functional_validators import AfterValidator


class NotesSerializer(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[int]= None
    user_id: int
    title: str
    description: str
    is_archive: Optional[bool] = False
    is_trash: Optional[bool] = False
    color: Optional[str] = None
    reminder: Optional[Annotated[datetime, AfterValidator(str)]] = None
    image: Optional[str] = None