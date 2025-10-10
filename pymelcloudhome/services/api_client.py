"""API client for handling HTTP requests to MELCloud Home."""

import logging
from typing import Any, Dict, Optional

from aiohttp import ClientError, ClientSession

from ..config import BASE_URL, DEFAULT_HEADERS
from ..errors import ApiError

logger = logging.getLogger(__name__)


class ApiClient:
    """Handles HTTP requests to the MELCloud Home API."""

    def __init__(self, session: ClientSession):
        """Initialize the API client with a session."""
        self._session = session
        self._base_headers = DEFAULT_HEADERS.copy()

    async def make_request(
        self, 
        method: str, 
        endpoint: str, 
        headers: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint path
            headers: Additional headers to include
            **kwargs: Additional arguments for the request
            
        Returns:
            The JSON response as a dictionary
            
        Raises:
            ApiError: If the request fails
        """
        request_headers = self._base_headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            logger.debug("Making API request: %s %s", method.upper(), endpoint)
            response = await self._session.request(
                method, 
                endpoint, 
                headers=request_headers,
                **kwargs
            )

            if not response.ok:
                error_message = await self._extract_error_message(response)
                logger.error(
                    "API request failed: %s %s - Status: %s, Error: %s", 
                    method.upper(), endpoint, response.status, error_message
                )
                raise ApiError(response.status, error_message)

            logger.debug("API request successful: %s %s", method.upper(), endpoint)
            return await response.json()

        except ClientError as e:
            status = getattr(e, "status", -1)
            logger.error("Client error during API request: %s", e)
            raise ApiError(status, str(e)) from e

    async def _extract_error_message(self, response) -> str:
        """Extract error message from failed response."""
        try:
            return await response.json()
        except ClientError:
            return await response.text()

    def is_session_expired(self, status_code: int) -> bool:
        """Check if the status code indicates session expiry."""
        return status_code == 401