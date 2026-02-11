from collections.abc import Awaitable, Callable
from typing import TypeVar

from pydantic import ImportString


TDep = TypeVar("TDep")
DepCallable = Callable[..., TDep | Awaitable[TDep]]
ZionImportString = ImportString[DepCallable[TDep]]
