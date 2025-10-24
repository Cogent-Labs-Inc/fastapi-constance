from typing import Optional

from sqlmodel import Field, SQLModel


class ConstanceConfig(SQLModel, table=True):
    key: str = Field(primary_key=True, index=True)
    default_value: str
    value: str
    description: Optional[str] = Field(default=None, nullable=True)
    is_admin_modified: bool = Field(
        default=False,
        description=(
            "Indicates whether this setting has been manually modified by an admin. "
            "If True, default value updates from CONFIG will not overwrite the admin-set value."
        ),
    )
