from pydantic import BaseModel, ConfigDict


class ErrorDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    error: str | None = None
    message: str | None = None
    details: list[str] | None = None

