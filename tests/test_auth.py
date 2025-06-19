"""Tests for the authentication module."""

from unittest.mock import Mock, patch

from athena_client.auth import build_headers


class TestAuth:
    """Test cases for the authentication module."""

    def test_build_headers_no_auth(self):
        """Test building headers without authentication."""
        with patch("athena_client.auth.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_TOKEN = None
            mock_settings.ATHENA_CLIENT_ID = None
            mock_settings.ATHENA_PRIVATE_KEY = None
            mock_get_settings.return_value = mock_settings

            headers = build_headers("GET", "https://api.example.com/test", b"")

            assert headers == {}

    def test_build_headers_with_token(self):
        """Test building headers with Bearer token authentication."""
        with patch("athena_client.auth.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_TOKEN = "test-token"
            mock_settings.ATHENA_CLIENT_ID = "test-client"
            mock_settings.ATHENA_PRIVATE_KEY = None
            mock_get_settings.return_value = mock_settings

            headers = build_headers("GET", "https://api.example.com/test", b"")

            assert headers["X-Athena-Auth"] == "Bearer test-token"
            assert headers["X-Athena-Client-Id"] == "test-client"

    def test_build_headers_with_token_no_client_id(self):
        """Test building headers with token but no client ID."""
        with patch("athena_client.auth.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_TOKEN = "test-token"
            mock_settings.ATHENA_CLIENT_ID = None
            mock_settings.ATHENA_PRIVATE_KEY = None
            mock_get_settings.return_value = mock_settings

            headers = build_headers("GET", "https://api.example.com/test", b"")

            assert headers["X-Athena-Auth"] == "Bearer test-token"
            assert headers["X-Athena-Client-Id"] == "athena-client"

    def test_build_headers_with_hmac(self):
        """Test building headers with HMAC authentication."""
        with patch("athena_client.auth.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_TOKEN = None
            mock_settings.ATHENA_CLIENT_ID = None
            mock_settings.ATHENA_PRIVATE_KEY = (
                "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----"
            )
            mock_get_settings.return_value = mock_settings

            # Mock the imports that happen inside build_headers
            mock_datetime = Mock()
            mock_datetime.utcnow.return_value.strftime.return_value = (
                "2023-01-01T00:00:00Z"
            )

            mock_b64encode = Mock()
            mock_b64encode.return_value.decode.return_value = "test-signature"

            mock_serialization = Mock()
            mock_key = Mock()
            mock_serialization.load_pem_private_key.return_value = mock_key
            mock_key.sign.return_value = b"test-signature"

            mock_hashes = Mock()
            mock_hashes.SHA256.return_value = "sha256"

            with (
                patch("athena_client.auth.datetime", mock_datetime),
                patch("athena_client.auth.b64encode", mock_b64encode),
            ):
                headers = build_headers(
                    "GET",
                    "https://api.example.com/test",
                    b"",
                    serialization_module=mock_serialization,
                    hashes_module=mock_hashes,
                )
                assert "X-Athena-Nonce" in headers
                assert "X-Athena-Hmac" in headers
                assert headers["X-Athena-Nonce"] == "2023-01-01T00:00:00Z"
                assert headers["X-Athena-Hmac"] == "test-signature"

    def test_build_headers_with_token_and_hmac(self):
        """Test building headers with both token and HMAC authentication."""
        with patch("athena_client.auth.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_TOKEN = "test-token"
            mock_settings.ATHENA_CLIENT_ID = "test-client"
            mock_settings.ATHENA_PRIVATE_KEY = (
                "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----"
            )
            mock_get_settings.return_value = mock_settings

            # Mock the imports that happen inside build_headers
            mock_datetime = Mock()
            mock_datetime.utcnow.return_value.strftime.return_value = (
                "2023-01-01T00:00:00Z"
            )

            mock_b64encode = Mock()
            mock_b64encode.return_value.decode.return_value = "test-signature"

            mock_serialization = Mock()
            mock_key = Mock()
            mock_serialization.load_pem_private_key.return_value = mock_key
            mock_key.sign.return_value = b"test-signature"

            mock_hashes = Mock()
            mock_hashes.SHA256.return_value = "sha256"

            with (
                patch("athena_client.auth.datetime", mock_datetime),
                patch("athena_client.auth.b64encode", mock_b64encode),
            ):
                build_headers(
                    "POST",
                    "https://api.example.com/test",
                    b"test-body",
                    serialization_module=mock_serialization,
                    hashes_module=mock_hashes,
                )
                # Verify the signing string includes the body
                expected_to_sign = "POST\nhttps://api.example.com/test\n\n2023-01-01T00:00:00Z\ntest-body"
                mock_key.sign.assert_called_once_with(
                    expected_to_sign.encode(), "sha256"
                )

    def test_build_headers_hmac_cryptography_import_error(self):
        """Test HMAC authentication when cryptography is not available."""
        with patch("athena_client.auth.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_TOKEN = None
            mock_settings.ATHENA_CLIENT_ID = None
            mock_settings.ATHENA_PRIVATE_KEY = "test-key"
            mock_get_settings.return_value = mock_settings

            # Patch sys.modules to simulate ImportError for cryptography and submodules
            import sys

            with patch.dict(
                sys.modules,
                {"cryptography": None, "cryptography.hazmat.primitives": None},
            ):
                with patch("athena_client.auth.logger") as mock_logger:
                    headers = build_headers("GET", "https://api.example.com/test", b"")
                    assert headers == {}
                    mock_logger.warning.assert_called_once()
                    mock_logger.warning.assert_called_once()

    def test_build_headers_hmac_exception(self):
        """Test HMAC authentication when an exception occurs."""
        with patch("athena_client.auth.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_TOKEN = None
            mock_settings.ATHENA_CLIENT_ID = None
            mock_settings.ATHENA_PRIVATE_KEY = "invalid-key"
            mock_get_settings.return_value = mock_settings

            # Mock the imports that happen inside build_headers
            mock_datetime = Mock()
            mock_datetime.utcnow.return_value.strftime.return_value = (
                "2023-01-01T00:00:00Z"
            )

            mock_serialization = Mock()
            mock_serialization.load_pem_private_key.side_effect = Exception(
                "Invalid key"
            )

            with patch("athena_client.auth.datetime", mock_datetime):
                with patch("athena_client.auth.logger") as mock_logger:
                    headers = build_headers(
                        "GET",
                        "https://api.example.com/test",
                        b"",
                        serialization_module=mock_serialization,
                        hashes_module=Mock(),
                    )

                    assert headers == {}
                    mock_logger.error.assert_called_once()

    def test_build_headers_different_methods(self):
        """Test building headers with different HTTP methods."""
        with patch("athena_client.auth.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_TOKEN = None
            mock_settings.ATHENA_CLIENT_ID = None
            mock_settings.ATHENA_PRIVATE_KEY = (
                "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----"
            )
            mock_get_settings.return_value = mock_settings

            # Mock the imports that happen inside build_headers
            mock_datetime = Mock()
            mock_datetime.utcnow.return_value.strftime.return_value = (
                "2023-01-01T00:00:00Z"
            )

            mock_b64encode = Mock()
            mock_b64encode.return_value.decode.return_value = "test-signature"

            mock_serialization = Mock()
            mock_key = Mock()
            mock_serialization.load_pem_private_key.return_value = mock_key
            mock_key.sign.return_value = b"test-signature"

            mock_hashes = Mock()
            mock_hashes.SHA256.return_value = "sha256"

            with (
                patch("athena_client.auth.datetime", mock_datetime),
                patch("athena_client.auth.b64encode", mock_b64encode),
            ):
                # Test different HTTP methods
                for method in ["GET", "POST", "PUT", "DELETE"]:
                    headers = build_headers(
                        method,
                        "https://api.example.com/test",
                        b"",
                        serialization_module=mock_serialization,
                        hashes_module=mock_hashes,
                    )
                    assert "X-Athena-Nonce" in headers
                    assert "X-Athena-Hmac" in headers
                    # Verify the signing string includes the method
                    expected_to_sign = f"{method}\nhttps://api.example.com/test\n\n2023-01-01T00:00:00Z\n"
                    mock_key.sign.assert_called_with(
                        expected_to_sign.encode(), "sha256"
                    )

    def test_build_headers_with_body(self):
        """Test building headers with request body."""
        with patch("athena_client.auth.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_TOKEN = None
            mock_settings.ATHENA_CLIENT_ID = None
            mock_settings.ATHENA_PRIVATE_KEY = (
                "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----"
            )
            mock_get_settings.return_value = mock_settings

            # Mock the imports that happen inside build_headers
            mock_datetime = Mock()
            mock_datetime.utcnow.return_value.strftime.return_value = (
                "2023-01-01T00:00:00Z"
            )

            mock_b64encode = Mock()
            mock_b64encode.return_value.decode.return_value = "test-signature"

            mock_serialization = Mock()
            mock_key = Mock()
            mock_serialization.load_pem_private_key.return_value = mock_key
            mock_key.sign.return_value = b"test-signature"

            mock_hashes = Mock()
            mock_hashes.SHA256.return_value = "sha256"

            with (
                patch("athena_client.auth.datetime", mock_datetime),
                patch("athena_client.auth.b64encode", mock_b64encode),
            ):
                build_headers(
                    "POST",
                    "https://api.example.com/test",
                    b"test-body",
                    serialization_module=mock_serialization,
                    hashes_module=mock_hashes,
                )
                # Verify the signing string includes the body
                expected_to_sign = "POST\nhttps://api.example.com/test\n\n2023-01-01T00:00:00Z\ntest-body"
                mock_key.sign.assert_called_once_with(
                    expected_to_sign.encode(), "sha256"
                )

    def test_build_headers_empty_body(self):
        """Test building headers with empty body."""
        with patch("athena_client.auth.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_TOKEN = None
            mock_settings.ATHENA_CLIENT_ID = None
            mock_settings.ATHENA_PRIVATE_KEY = (
                "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----"
            )
            mock_get_settings.return_value = mock_settings

            # Mock the imports that happen inside build_headers
            mock_datetime = Mock()
            mock_datetime.utcnow.return_value.strftime.return_value = (
                "2023-01-01T00:00:00Z"
            )

            mock_b64encode = Mock()
            mock_b64encode.return_value.decode.return_value = "test-signature"

            mock_serialization = Mock()
            mock_key = Mock()
            mock_serialization.load_pem_private_key.return_value = mock_key
            mock_key.sign.return_value = b"test-signature"

            mock_hashes = Mock()
            mock_hashes.SHA256.return_value = "sha256"

            with (
                patch("athena_client.auth.datetime", mock_datetime),
                patch("athena_client.auth.b64encode", mock_b64encode),
            ):
                build_headers(
                    "GET",
                    "https://api.example.com/test",
                    b"",
                    serialization_module=mock_serialization,
                    hashes_module=mock_hashes,
                )
                # Verify the signing string includes empty body
                expected_to_sign = (
                    "GET\nhttps://api.example.com/test\n\n2023-01-01T00:00:00Z\n"
                )
                mock_key.sign.assert_called_once_with(
                    expected_to_sign.encode(), "sha256"
                )
