"""
ULID (Universally Unique Lexicographically Sortable Identifier) implementation
for SQLAlchemy and Pydantic models.
"""
from typing import Any
from ulid import ULID
from sqlalchemy.types import TypeDecorator, String
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class ULIDType(TypeDecorator):
    """SQLAlchemy type for ULID fields."""
    
    impl = String
    cache_ok = True
    
    def __init__(self, length: int = 26, **kwargs: Any):
        super().__init__(length=length, **kwargs)
    
    def process_bind_param(self, value: Any, dialect: Any) -> str | None:
        """Convert ULID object to string for database storage."""
        if value is None:
            return None
        if isinstance(value, ULID):
            return str(value)
        if isinstance(value, str):
            # Validate that it's a valid ULID string
            try:
                ULID.from_str(value)
                return value
            except ValueError:
                raise ValueError(f"Invalid ULID string: {value}")
        raise ValueError(f"Cannot convert {type(value)} to ULID")
    
    def process_result_value(self, value: str | None, dialect: Any) -> ULID | None:
        """Convert database string to ULID object."""
        if value is None:
            return None
        return ULID.from_str(value)
    
    def process_literal_param(self, value: Any, dialect: Any) -> str | None:
        """Process literal parameters."""
        return self.process_bind_param(value, dialect)


def ulid_schema(schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
    """Pydantic JSON schema for ULID fields."""
    json_schema = handler(schema)
    json_schema.update(
        type="string",
        pattern=r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$",
        description="ULID (Universally Unique Lexicographically Sortable Identifier)",
        examples=["01ARZ3NDEKTSV4RRFFQ69G5FAV"]
    )
    return json_schema


def generate_ulid() -> str:
    """Generate a new ULID string."""
    return str(ULID())


def ulid_from_str(ulid_str: str) -> ULID:
    """Create ULID object from string."""
    return ULID.from_str(ulid_str)


def ulid_from_timestamp(timestamp_ms: int) -> ULID:
    """Create ULID object from timestamp in milliseconds."""
    return ULID.from_timestamp(timestamp_ms)
