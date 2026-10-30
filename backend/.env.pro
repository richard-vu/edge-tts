# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./data/edge_tts.db

# Edge TTS Default Configuration
TTS_DEFAULT_LOCALE=en-US
TTS_DEFAULT_VOICE=en-US-AndrewNeural
TTS_DEFAULT_RATE=+0%
TTS_DEFAULT_VOLUME=+0%
TTS_DEFAULT_PITCH=+0Hz

# CORS Configuration
CORS_ALLOW_ORIGINS=http://host.docker.internal:9101
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
