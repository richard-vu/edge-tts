import math
from collections.abc import Callable, Sequence
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
    )

    content: list[T] = Field(default_factory=list)
    page_no: int = 0
    page_size: int = 0
    total_elements: int = 0
    total_pages: int = 0

    @field_validator("content", mode="before")
    @classmethod
    def ensure_content_not_none(cls, value: list[T] | None) -> list[T]:
        return [] if value is None else list(value)

    @classmethod
    def of(
        cls,
        content: Sequence[Any] | None,
        page_no: int,
        page_size: int,
        total_elements: int,
        mapper: Callable[[Any], T] | None = None,
    ) -> "PageResponse[T]":
        items = [] if content is None else list(content)
        mapped_items: list[T] = [mapper(item) for item in items] if mapper else items
        total_pages = math.ceil(total_elements / page_size) if page_size > 0 else 0

        return cls(
            content=mapped_items,
            page_no=page_no,
            page_size=page_size,
            total_elements=total_elements,
            total_pages=total_pages,
        )

