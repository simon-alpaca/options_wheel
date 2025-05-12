USER_AGENT = "OPTIONS-WHEEL"

class UserAgentMixin:
    def _get_default_headers(self) -> dict:
        headers = self._get_auth_headers()
        headers["User-Agent"] = USER_AGENT
        return headers
