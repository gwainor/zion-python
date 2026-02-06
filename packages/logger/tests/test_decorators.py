from dataclasses import dataclass

import pytest
from structlog.testing import CapturedCall, CapturingLogger
from zion_logger.decorators import log


class AsyncCapturingLogger(CapturingLogger):
    """A capturing logger that properly handles async logging methods."""

    def __getattr__(self, name: str):
        """Override to make async methods actually async."""
        if name.startswith("a") and name[1:] in ["debug", "info", "warning", "error"]:
            # This is an async logging method
            async def async_log(*args, **kwargs):
                self.calls.append(
                    CapturedCall(method_name=name, args=args, kwargs=kwargs)
                )
                return None

            return async_log
        return super().__getattr__(name)


@dataclass
class User:
    name: str
    age: int


class CustomError(Exception):
    pass


class TestLogDecoratorSync:
    """Test the log decorator with synchronous functions."""

    def test_basic_function_logging(self):
        """Test that a basic function logs input and output."""
        logger = CapturingLogger()

        @log(logger=logger)
        def add(a: int, b: int) -> int:
            return a + b

        result = add(2, 3)

        assert result == 5
        assert len(logger.calls) == 1
        assert logger.calls[0].method_name == "debug"
        assert "Called: add" in logger.calls[0].args[0]
        assert logger.calls[0].kwargs["input"] == {"a": 2, "b": 3}
        assert logger.calls[0].kwargs["return_value"] == 5

    def test_function_with_kwargs(self):
        """Test logging with keyword arguments."""
        logger = CapturingLogger()

        @log(logger=logger)
        def greet(name: str, greeting: str = "Hello"):
            return f"{greeting}, {name}!"

        result = greet("Alice", greeting="Hi")

        assert result == "Hi, Alice!"
        assert len(logger.calls) == 1
        assert logger.calls[0].kwargs["input"] == {"name": "Alice", "greeting": "Hi"}

    def test_sanitize_params(self):
        """Test that specified parameters are sanitized."""
        logger = CapturingLogger()

        @log(logger=logger, sanitize_params=["password"])
        def login(username: str, password: str):
            return f"Logged in as {username} with password {password}"

        result = login("alice", "secret123")

        assert result == "Logged in as alice with password secret123"
        assert len(logger.calls) == 1
        assert logger.calls[0].kwargs["input"]["username"] == "alice"
        assert logger.calls[0].kwargs["input"]["password"] == "*" * 10

    def test_dataclass_parameter(self):
        """Test that dataclass parameters are represented as strings."""
        logger = CapturingLogger()

        @log(logger=logger)
        def process_user(user: User):
            return f"Processing {user.name}"

        user = User(name="Bob", age=30)
        result = process_user(user)

        assert result == "Processing Bob"
        assert len(logger.calls) == 1
        assert "User" in logger.calls[0].kwargs["input"]["user"]
        assert "Bob" in logger.calls[0].kwargs["input"]["user"]

    def test_expected_error(self):
        """Test that expected errors are logged at debug/info level."""
        logger = CapturingLogger()

        @log(logger=logger, expected_errors=[CustomError])
        def may_fail(should_fail: bool):
            if should_fail:
                raise CustomError("Expected failure")
            return "success"

        # Test success case
        result = may_fail(False)
        assert result == "success"
        assert len(logger.calls) == 1
        assert "Called: may_fail" in logger.calls[0].args[0]

        # Test expected error case
        with pytest.raises(CustomError):
            may_fail(True)

        assert len(logger.calls) == 2
        assert "raised expected error" in logger.calls[1].args[0]
        assert logger.calls[1].kwargs["error"] == "Expected failure"
        assert logger.calls[1].method_name == "debug"

    def test_unexpected_error(self):
        """Test that unexpected errors are logged at error level."""
        logger = CapturingLogger()

        @log(logger=logger, expected_errors=[CustomError])
        def may_fail(should_fail: bool):
            if should_fail:
                raise ValueError("Unexpected failure")
            return "success"

        with pytest.raises(ValueError):
            may_fail(True)

        assert len(logger.calls) == 1
        assert "raised unexpected error" in logger.calls[0].args[0]
        assert logger.calls[0].kwargs["error"] == "Unexpected failure"
        assert logger.calls[0].method_name == "error"

    def test_info_log_level(self):
        """Test that log level can be set to info."""
        logger = CapturingLogger()

        @log(logger=logger, level="info")
        def info_function():
            return "result"

        result = info_function()

        assert result == "result"
        assert len(logger.calls) == 1
        assert logger.calls[0].method_name == "info"

    def test_class_method(self):
        """Test that class methods are logged with class name."""
        logger = CapturingLogger()

        class Calculator:
            @log(logger=logger)
            def multiply(self, a: int, b: int) -> int:
                return a * b

        calc = Calculator()
        result = calc.multiply(4, 5)

        assert result == 20
        assert len(logger.calls) == 1
        assert "Calculator::multiply" in logger.calls[0].args[0]
        # self should be in the parameters
        assert "self" in logger.calls[0].kwargs["input"]


class TestLogDecoratorAsync:
    """Test the log decorator with asynchronous functions."""

    @pytest.mark.asyncio
    async def test_basic_async_function(self):
        """Test that async functions are logged correctly."""
        logger = AsyncCapturingLogger()

        @log(logger=logger)
        async def fetch_data(id: int) -> str:
            return f"data_{id}"

        result = await fetch_data(42)

        assert result == "data_42"
        assert len(logger.calls) == 1
        assert logger.calls[0].method_name == "adebug"
        assert "Called: fetch_data" in logger.calls[0].args[0]
        assert logger.calls[0].kwargs["input"] == {"id": 42}
        assert logger.calls[0].kwargs["return_value"] == "data_42"

    @pytest.mark.asyncio
    async def test_async_with_sanitization(self):
        """Test parameter sanitization in async functions."""
        logger = AsyncCapturingLogger()

        @log(logger=logger, sanitize_params=["token"])
        async def api_call(endpoint: str, token: str):
            return f"Called {endpoint} with token {token}"

        result = await api_call("/users", "secret_token")

        assert result == "Called /users with token secret_token"
        assert len(logger.calls) == 1
        assert logger.calls[0].kwargs["input"]["endpoint"] == "/users"
        assert logger.calls[0].kwargs["input"]["token"] == "*" * 10

    @pytest.mark.asyncio
    async def test_async_expected_error(self):
        """Test expected error handling in async functions."""
        logger = AsyncCapturingLogger()

        @log(logger=logger, expected_errors=[CustomError])
        async def async_may_fail(should_fail: bool):
            if should_fail:
                raise CustomError("Async expected failure")
            return "success"

        # Test success
        result = await async_may_fail(False)
        assert result == "success"

        # Test expected error
        with pytest.raises(CustomError):
            await async_may_fail(True)

        assert len(logger.calls) == 2
        assert "raised expected error" in logger.calls[1].args[0]

    @pytest.mark.asyncio
    async def test_async_unexpected_error(self):
        """Test unexpected error handling in async functions."""
        logger = AsyncCapturingLogger()

        @log(logger=logger, expected_errors=[CustomError])
        async def async_may_fail(should_fail: bool):
            if should_fail:
                raise ValueError("Async unexpected failure")
            return "success"

        with pytest.raises(ValueError):
            await async_may_fail(True)

        assert len(logger.calls) == 1
        assert "raised unexpected error" in logger.calls[0].args[0]
        assert logger.calls[0].method_name == "aerror"

    @pytest.mark.asyncio
    async def test_async_class_method(self):
        """Test async class methods."""
        logger = AsyncCapturingLogger()

        class AsyncService:
            @log(logger=logger)
            async def process(self, value: int) -> int:
                return value * 2

        service = AsyncService()
        result = await service.process(10)

        assert result == 20
        assert len(logger.calls) == 1
        assert "AsyncService::process" in logger.calls[0].args[0]

    @pytest.mark.asyncio
    async def test_async_info_level(self):
        """Test async functions with info log level."""
        logger = AsyncCapturingLogger()

        @log(logger=logger, level="info")
        async def async_info():
            return "info result"

        result = await async_info()

        assert result == "info result"
        assert len(logger.calls) == 1
        assert logger.calls[0].method_name == "ainfo"


class TestLogDecoratorEdgeCases:
    """Test edge cases and special scenarios."""

    def test_function_with_no_args(self):
        """Test function with no arguments."""
        logger = CapturingLogger()

        @log(logger=logger)
        def no_args():
            return "result"

        result = no_args()

        assert result == "result"
        assert len(logger.calls) == 1
        assert logger.calls[0].kwargs["input"] == {}

    def test_function_with_default_args(self):
        """Test that default arguments are included."""
        logger = CapturingLogger()

        @log(logger=logger)
        def with_defaults(a: int, b: int = 10, c: int = 20):
            return a + b + c

        result = with_defaults(5)

        assert result == 35
        assert len(logger.calls) == 1
        # bind_partial with apply_defaults should include default values
        assert logger.calls[0].kwargs["input"]["a"] == 5
        assert logger.calls[0].kwargs["input"]["b"] == 10
        assert logger.calls[0].kwargs["input"]["c"] == 20

    def test_multiple_expected_errors(self):
        """Test handling multiple expected error types."""
        logger = CapturingLogger()

        @log(logger=logger, expected_errors=[CustomError, ValueError])
        def multi_error(error_type: str):
            if error_type == "custom":
                raise CustomError("Custom")
            elif error_type == "value":
                raise ValueError("Value")
            return "success"

        # Test custom error
        with pytest.raises(CustomError):
            multi_error("custom")

        assert "raised expected error" in logger.calls[0].args[0]

        # Test value error
        with pytest.raises(ValueError):
            multi_error("value")

        assert "raised expected error" in logger.calls[1].args[0]

    def test_none_return_value(self):
        """Test function that returns None."""
        logger = CapturingLogger()

        @log(logger=logger)
        def returns_none():
            pass

        result = returns_none()

        assert result is None
        assert len(logger.calls) == 1
        assert logger.calls[0].kwargs["return_value"] is None

    def test_empty_sanitize_list(self):
        """Test with empty sanitize list."""
        logger = CapturingLogger()

        @log(logger=logger, sanitize_params=[])
        def no_sanitize(password: str):
            return f"ok {password}"

        result = no_sanitize("secret")

        assert result == "ok secret"
        assert logger.calls[0].kwargs["input"]["password"] == "secret"

    def test_sanitize_nonexistent_param(self):
        """Test sanitizing a parameter that doesn't exist."""
        logger = CapturingLogger()

        @log(logger=logger, sanitize_params=["nonexistent"])
        def func(a: int):
            return a * 2

        result = func(5)

        assert result == 10
        assert logger.calls[0].kwargs["input"]["a"] == 5

    def test_preserves_function_metadata(self):
        """Test that the decorator preserves function metadata."""

        @log()
        def documented_function(x: int) -> int:
            """This is a documented function."""
            return x * 2

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a documented function."

    def test_exception_traceback_preserved(self):
        """Test that exception tracebacks are preserved."""
        logger = CapturingLogger()

        @log(logger=logger)
        def raise_error():
            raise ValueError("Test error")

        try:
            raise_error()
        except ValueError as e:
            # Check that the exception was raised
            assert str(e) == "Test error"
            # The traceback should include raise_error in it
            import traceback

            tb = traceback.format_exc()
            assert "raise_error" in tb
