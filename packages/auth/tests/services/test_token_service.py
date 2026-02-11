import datetime as dt

import pytest
from jose import jwt

from zion_auth.services.token import TokenService, TokenType
from zion_auth.settings import settings


def generate_token(
    data: dict | None = None,
    delta: dt.timedelta | None = None,
    expire: dt.datetime | None = None,
    token_type: TokenType | str | None = None,
):
    data = data or {"sub": "test"}
    delta = delta or dt.timedelta(days=1)
    expire = expire or dt.datetime.now(dt.UTC).replace(tzinfo=None) + delta
    token_type = token_type or TokenType.ACCESS

    to_encode = data.copy()
    to_encode.update({"exp": expire, "token_type": token_type})
    token = jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.token_algorithm,
    )
    return token


@pytest.mark.asyncio
async def test_create_access_token_without_expire_delta_sucess():
    # Given
    token_service = TokenService()
    data = {"sub": "test"}

    # When
    access_token = await token_service.create_access_token(data)

    # Then
    assert isinstance(access_token, str)
    token_data = await token_service.verify(access_token, TokenType.ACCESS)
    assert token_data is not None
    assert token_data.public_id == data["sub"]


@pytest.mark.asyncio
async def test_create_access_token_with_expire_delta_success():
    # Given
    token_service = TokenService()
    data = {"sub": "test"}
    expires_delta = dt.timedelta(days=1)

    # When
    access_token = await token_service.create_access_token(
        data, expires_delta=expires_delta
    )

    # Then
    assert isinstance(access_token, str)
    token_data = await token_service.verify(access_token, TokenType.ACCESS)
    assert token_data is not None
    assert token_data.public_id == data["sub"]


@pytest.mark.asyncio
async def test_create_refresh_token_without_expire_delta_sucess():
    # Given
    token_service = TokenService()
    data = {"sub": "test"}

    # When
    refresh_token = await token_service.create_refresh_token(data)

    # Then
    assert isinstance(refresh_token, str)
    token_data = await token_service.verify(refresh_token, TokenType.REFRESH)
    assert token_data is not None
    assert token_data.public_id == data["sub"]


@pytest.mark.asyncio
async def test_create_refresh_token_with_expire_delta_success():
    # Given
    token_service = TokenService()
    data = {"sub": "test"}
    expires_delta = dt.timedelta(days=1)

    # When
    refresh_token = await token_service.create_refresh_token(
        data, expires_delta=expires_delta
    )

    # Then
    assert isinstance(refresh_token, str)
    token_data = await token_service.verify(refresh_token, TokenType.REFRESH)
    assert token_data is not None
    assert token_data.public_id == data["sub"]


@pytest.mark.asyncio
async def test_create_token_raises_value_error_with_unknown_token_type():
    # Given
    token_service = TokenService()
    data = {"sub": "test"}
    expires_delta = dt.timedelta(days=1)

    # When / Then
    with pytest.raises(ValueError):
        await token_service._create("unknown_type", data)  # ty: ignore[invalid-argument-type]

    with pytest.raises(ValueError):
        await token_service._create("unknown_type", data, expires_delta=expires_delta)  # ty: ignore[invalid-argument-type]


@pytest.mark.asyncio
@pytest.mark.parametrize("token_type", [TokenType.ACCESS, TokenType.REFRESH])
async def test_verify_returns_none_with_expired_access_token(token_type):
    # Given
    token_service = TokenService()
    delta = dt.timedelta(days=1)
    expire = dt.datetime.now(dt.UTC).replace(tzinfo=None) - delta
    token = generate_token(expire=expire, token_type=token_type)

    # When
    token_data = await token_service.verify(token, token_type)

    # Then
    assert token_data is None


@pytest.mark.asyncio
async def test_verify_returns_none_with_unknown_token_type():
    # Given
    token_service = TokenService()
    token_type = "unknown_type"
    token = generate_token(token_type=token_type)

    # When
    token_data = await token_service.verify(token, token_type)  # ty: ignore[invalid-argument-type]

    # Then
    assert token_data is None
