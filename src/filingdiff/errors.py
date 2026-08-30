"""Domain-specific exceptions with user-facing messages."""


class FilingDiffError(Exception):
    """Base class for expected FilingDiff failures."""


class ConfigurationError(FilingDiffError):
    """Raised when required runtime configuration is missing or invalid."""


class UnsupportedTickerError(FilingDiffError):
    """Raised when a ticker is outside the version-one company universe."""


class SecRequestError(FilingDiffError):
    """Raised when official SEC data cannot be retrieved."""


class SecResponseError(FilingDiffError):
    """Raised when an SEC response does not have the expected data shape."""


class InsufficientFilingsError(FilingDiffError):
    """Raised when fewer than two exact-form 10-Q filings are available."""

