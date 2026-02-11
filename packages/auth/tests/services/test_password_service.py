import pytest

from zion_auth.services.password import PasswordService


@pytest.mark.asyncio
async def test_hash_password_success():
    # Given
    service = PasswordService()
    password = "test_password_123"

    # When
    hashed_password = await service.hash(password)

    # Then
    assert isinstance(hashed_password, str)
    assert hashed_password != password
    assert len(hashed_password) > 0


@pytest.mark.asyncio
async def test_hash_generates_different_hashes_for_same_password():
    # Given
    password_service = PasswordService()
    plain_password = "test_password_123"

    # When
    hashed_password_1 = await password_service.hash(plain_password)
    hashed_password_2 = await password_service.hash(plain_password)

    # Then
    assert hashed_password_1 != hashed_password_2


@pytest.mark.asyncio
async def test_verify_password_with_correct_password_success():
    # Given
    password_service = PasswordService()
    plain_password = "test_password_123"
    hashed_password = await password_service.hash(plain_password)

    # When
    is_valid = await password_service.verify(plain_password, hashed_password)

    # Then
    assert is_valid is True


@pytest.mark.asyncio
async def test_verify_password_with_incorrect_password_fails():
    # Given
    password_service = PasswordService()
    plain_password = "test_password_123"
    wrong_password = "wrong_password_456"
    hashed_password = await password_service.hash(plain_password)

    # When
    is_valid = await password_service.verify(wrong_password, hashed_password)

    # Then
    assert is_valid is False


@pytest.mark.asyncio
async def test_verify_password_with_empty_password_fails():
    # Given
    password_service = PasswordService()
    plain_password = "test_password_123"
    empty_password = ""
    hashed_password = await password_service.hash(plain_password)

    # When
    is_valid = await password_service.verify(empty_password, hashed_password)

    # Then
    assert is_valid is False


@pytest.mark.asyncio
async def test_hash_empty_password_success():
    # Given
    password_service = PasswordService()
    empty_password = ""

    # When
    hashed_password = await password_service.hash(empty_password)

    # Then
    assert isinstance(hashed_password, str)
    assert len(hashed_password) > 0
