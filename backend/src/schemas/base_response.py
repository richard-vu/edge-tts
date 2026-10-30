from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_serializer

from src.schemas.error_details import ErrorDetails

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(populate_by_name=True)

    success: bool
    code: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: T | None = None
    errors: list[ErrorDetails] | None = None

    @model_serializer(mode="wrap")
    def _serialize_non_null(self, handler: Any) -> dict[str, Any]:
        """Exclude fields with None values when serializing (equivalent to @JsonInclude(Include.NON_NULL))."""
        result: dict[str, Any] = handler(self)
        return {k: v for k, v in result.items() if v is not None}

    @classmethod
    def ok(
        cls,
        data: T | None = None,
        message: str = "Request processed successfully",
    ) -> "BaseResponse[T]":
        return cls(
            success=True,
            code="SUCCESS",
            message=message,
            data=data,
        )

    @classmethod
    def created(
        cls,
        data: T | None = None,
        message: str = "Resource created successfully",
    ) -> "BaseResponse[T]":
        return cls(
            success=True,
            code="CREATED",
            message=message,
            data=data,
        )

    @classmethod
    def error(cls, code: str, message: str) -> "BaseResponse[Any]":
        return cls(
            success=False,
            code=code,
            message=message,
        )

    @classmethod
    def bad_request(cls, message: str) -> "BaseResponse[Any]":
        return cls.error("BAD_REQUEST", message)

    @classmethod
    def not_found(cls, message: str) -> "BaseResponse[Any]":
        return cls.error("NOT_FOUND", message)

    @classmethod
    def internal_error(cls, message: str) -> "BaseResponse[Any]":
        return cls.error("INTERNAL_ERROR", message)

    @classmethod
    def validation_error(
        cls,
        errors: list[ErrorDetails],
        message: str = "Validation failed",
    ) -> "BaseResponse[Any]":
        return cls(
            success=False,
            code="VALIDATION_ERROR",
            message=message,
            errors=errors,
        )

    def with_data(self, new_data: T) -> "BaseResponse[T]":
        return self.model_copy(update={"data": new_data})

    def with_errors(self, new_errors: list[ErrorDetails]) -> "BaseResponse[T]":
        return self.model_copy(update={"errors": new_errors})

