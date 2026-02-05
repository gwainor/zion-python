from pydantic import SecretStr

DB_DATABASE_URI = "sqlite+aiosqlite:///:memory:"

AUTH_SECRET_KEY = SecretStr("test-secret-key-for-testing-only")
