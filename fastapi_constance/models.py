from typing import Optional
from sqlmodel import SQLModel, Field

class ConstanceConfig(SQLModel, table=True):
    key: str = Field(primary_key=True, index=True)
    default_value: str
    value: str
    description: Optional[str] = Field(default=None, nullable=True)
    is_admin_modified: bool = Field(default=False)
