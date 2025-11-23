class WPToolsError(Exception):
    """Base exception for WP-Tools."""


class WPAuthenticationError(WPToolsError):
    """Raised when authentication against WordPress fails."""


class WPRequestError(WPToolsError):
    """Raised when a WordPress request fails."""
