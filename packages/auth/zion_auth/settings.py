from typing import Annotated

from annotated_doc import Doc
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from zion_auth.enums import CredentialType


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        extra="ignore",
        env_prefix="auth_",
    )

    service: Annotated[
        str,
        Doc(
            """
            The main orchestrator service.

            Necessary logic like login, register, verify is in this service.
            You must extend from ZionAuthService if you want to change some logic.
            """
        ),
    ] = "zion_auth.services.zion_auth.ZionAuthService"

    secret_key: Annotated[
        SecretStr,
        Doc(
            """
            Secret key for auth mechanism which is required and has to be a
            generated complex value.

            Example string generation:

            ```python
            import secrets

            print(secrets.token_urlsafe(32))
            ```
            """
        ),
    ] = Field(SecretStr("changethis"))

    credential_type: Annotated[
        CredentialType,
        Doc(
            """
            Determines which fields can be used when logging in the user.

            It can be:
            - `email` only allow login with email address
            - `username` only allow login with username
            - `both` allow loggin in with email or username
            """
        ),
    ] = CredentialType.EMAIL

    ##
    # Database Adapter Settings
    database_adapter: Annotated[
        str,
        Doc(
            """
            The Database Adapter Dependency

            The dependency function that returns an adapter that extends abstract class
            `zion_auth.protocols.DatabaseAdapterProtocol`.

            The module in the provided string must provide a function called `get_adapter`
            which returns the instance of the adapter.

            Zion provides following adapters:
            - SqlAlchemy: `zion_auth.adapters.sqlalchemy.SqlAlchemyAdapter`
            """
        ),
    ] = "zion_auth.adapters.sqlalchemy.SqlAlchemyAdapter"

    database_session_dep: Annotated[
        str | None,
        Doc(
            """
            Database session dependency

            SqlAlchemy requires the AsyncSession to make the necessary operations.
            This setting is required if SqlAlchemy adapter is being used.
            """
        ),
    ] = None

    sqlalchemy_base_import: Annotated[
        str,
        Doc(
            """
            SqlAlchemy Base Model Import

            If SqlAlchemy adapter is selected, the base model is needed to extend
            Zion Auth models from. This will give the ability to use generic methdos
            defined in the Base Model.
            """
        ),
    ] = ""

    ##
    # Password Settings
    password_service: Annotated[
        str,
        Doc(
            """
            Password Service Dependency

            Zion Auth provides a password service to hash and verify the passwords.
            If a different approach needed, it can be defined in here

            The dependency must return a service instance that extends from
            `zion_auth.protocols.PasswordServiceProtocol` in order to work with the system.
            """
        ),
    ] = "zion_auth.services.password.PasswordService"

    password_min_length: Annotated[
        int,
        Doc("Minimum length required for user passwords."),
    ] = 8
    password_max_length: Annotated[
        int,
        Doc("Maximum length allowed for user passwords."),
    ] = 40

    ##
    # Token Settings
    token_service: Annotated[
        str,
        Doc(
            """
            Password Service

            Zion Auth uses `jose.jwt` to generate and verify the tokens.
            If a different approach needed, it can be defined in here.

            The dependency must return a service instance that extends from
            `zion_auth.protocols.TokenServiceProtocol` in order to work with the system.
            """
        ),
    ] = "zion_auth.services.token.TokenService"

    token_algorithm: Annotated[
        str,
        Doc("The algorithm used to generate the tokens."),
    ] = "HS256"

    access_token_expire_minutes: Annotated[
        int,
        Doc("When will access token expire?"),
    ] = 30

    refresh_token_expire_days: Annotated[
        int,
        Doc("When will refresh token expire in days"),
    ] = 7

    oauth2_scheme_token_url: Annotated[
        str,
        Doc("The token url for the OAuth2PasswordBearer."),
    ] = "/api/v1/auth/login"

    ##
    # Validation Service
    validation_service: Annotated[
        str,
        Doc(
            """
            Validation Service

            Validation service has various uses like processing logged in user
            or found user with access token to ensure that user is valid to
            continue.
            """
        ),
    ] = "zion_auth.services.validation.ValidationService"

    user_validators: Annotated[
        list[str],
        Doc(
            """
            List of validators to run against user.

            It will run in the given order and stop execution as soon as a validator
            returns False or throws an exception.

            Only ValueError and AttributeError errors will be accounted as validation
            errors. Other errors will be treaded as unhandled errors.
            """
        ),
    ] = ["zion_auth.validators.user.is_active"]


settings = Settings()
