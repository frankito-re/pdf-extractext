from application.checksum import calculate_checksum

STATIC_CONTENT = b"pdf-extractext static test content"
EXPECTED_SHA256 = "3a5b2ee6379e440b13f8686c74b2a9e2f19650fd1c32c8a0de9fda7bcbc66a40"


def test_checksum_of_known_content_returns_expected_hash():
    result = calculate_checksum(STATIC_CONTENT)
    assert result == EXPECTED_SHA256
