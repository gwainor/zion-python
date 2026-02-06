from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from zion_db.engine import async_get_db

DbSessionDep = Annotated[AsyncSession, Depends(async_get_db)]
