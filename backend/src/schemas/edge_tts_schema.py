from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.core.config import settings


class SupportedLanguageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lang: str
    locales: list[str] = Field(default_factory=list)


class VoiceTagResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ContentCategories: list[str] = Field(default_factory=list)
    VoicePersonalities: list[str] = Field(default_factory=list)


class VoiceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    Name: str
    ShortName: str
    Gender: str
    Locale: str
    SuggestedCodec: str
    FriendlyName: str
    Status: str
    VoiceTag: VoiceTagResponse | None = None


class GenerateAudioRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=False,
        extra="forbid",
    )

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The text to convert to speech (Required, max 5000 characters)",
        examples=["Hello teachers, welcome to the lecture!"],
    )
    voice: str = Field(
        default=settings.TTS_DEFAULT_VOICE,
        min_length=1,
        description="The voice short name",
        examples=[settings.TTS_DEFAULT_VOICE],
    )
    rate: str = Field(
        default=settings.TTS_DEFAULT_RATE,
        description="Speaking speed modifier (e.g., '+10%', '-20%')",
        examples=[settings.TTS_DEFAULT_RATE],
    )
    volume: str = Field(
        default=settings.TTS_DEFAULT_VOLUME,
        description="Volume modifier (e.g., '+10%', '-10%')",
        examples=[settings.TTS_DEFAULT_VOLUME],
    )
    pitch: str = Field(
        default=settings.TTS_DEFAULT_PITCH,
        description="Pitch modifier (e.g., '+50Hz', '-20Hz')",
        examples=[settings.TTS_DEFAULT_PITCH],
    )


class TtsAudioResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
        from_attributes=True,
    )

    id: str
    text: str
    vn_meaning: str | None = None
    voice: str
    rate: str
    volume: str
    pitch: str
    file_name: str | None = None



