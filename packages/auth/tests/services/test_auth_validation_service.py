import pytest
from zion.auth.models import User
from zion.auth.services.auth_validation_service import AuthValidationService


def sync_validator_always_true(user: User) -> bool:
    return True


def sync_validator_always_false(user: User) -> bool:
    return False


def sync_validator_checks_is_active(user: User) -> bool:
    return user.is_active


def sync_validator_checks_email_verified(user: User) -> bool:
    return user.is_email_verified


async def async_validator_always_true(user: User) -> bool:
    return True


async def async_validator_always_false(user: User) -> bool:
    return False


async def async_validator_checks_is_active(user: User) -> bool:
    return user.is_active


async def async_validator_checks_email_verified(user: User) -> bool:
    return user.is_email_verified


@pytest.mark.asyncio
async def test_is_user_valid_with_no_validators_success():
    # Given
    auth_validation_service = AuthValidationService(user_validators=[])
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is True


@pytest.mark.asyncio
async def test_is_user_valid_with_single_sync_validator_success():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[sync_validator_always_true]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is True


@pytest.mark.asyncio
async def test_is_user_valid_with_single_sync_validator_fails():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[sync_validator_always_false]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_user_valid_with_single_async_validator_success():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[async_validator_always_true]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is True


@pytest.mark.asyncio
async def test_is_user_valid_with_single_async_validator_fails():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[async_validator_always_false]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_user_valid_with_multiple_sync_validators_all_pass_success():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[
            sync_validator_always_true,
            sync_validator_checks_is_active,
            sync_validator_checks_email_verified,
        ]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is True


@pytest.mark.asyncio
async def test_is_user_valid_with_multiple_sync_validators_one_fails():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[
            sync_validator_always_true,
            sync_validator_checks_is_active,
            sync_validator_checks_email_verified,
        ]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=False,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_user_valid_with_multiple_async_validators_all_pass_success():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[
            async_validator_always_true,
            async_validator_checks_is_active,
            async_validator_checks_email_verified,
        ]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is True


@pytest.mark.asyncio
async def test_is_user_valid_with_multiple_async_validators_one_fails():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[
            async_validator_always_true,
            async_validator_checks_is_active,
            async_validator_checks_email_verified,
        ]
    )
    user = User(
        hashed_password="hashed",
        is_active=False,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_user_valid_with_mixed_validators_all_pass_success():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[
            sync_validator_always_true,
            async_validator_always_true,
            sync_validator_checks_is_active,
            async_validator_checks_email_verified,
        ]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is True


@pytest.mark.asyncio
async def test_is_user_valid_with_mixed_validators_one_fails():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[
            sync_validator_always_true,
            async_validator_always_true,
            sync_validator_checks_is_active,
            async_validator_checks_email_verified,
        ]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=False,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_user_valid_stops_at_first_failure():
    # Given
    call_count = []

    def validator_1(user: User) -> bool:
        call_count.append(1)
        return True

    def validator_2(user: User) -> bool:
        call_count.append(2)
        return False

    def validator_3(user: User) -> bool:
        call_count.append(3)
        return True

    auth_validation_service = AuthValidationService(
        user_validators=[validator_1, validator_2, validator_3]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is False
    assert call_count == [1, 2]


@pytest.mark.asyncio
async def test_is_user_valid_with_inactive_user_fails():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[sync_validator_checks_is_active]
    )
    user = User(
        hashed_password="hashed",
        is_active=False,
        is_email_verified=True,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is False


@pytest.mark.asyncio
async def test_is_user_valid_with_unverified_email_fails():
    # Given
    auth_validation_service = AuthValidationService(
        user_validators=[sync_validator_checks_email_verified]
    )
    user = User(
        hashed_password="hashed",
        is_active=True,
        is_email_verified=False,
    )

    # When
    is_valid = await auth_validation_service.is_user_valid(user)

    # Then
    assert is_valid is False
