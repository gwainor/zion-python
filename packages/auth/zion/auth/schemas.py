from pydantic import BaseModel


class TokenData(BaseModel):
    credential: str
