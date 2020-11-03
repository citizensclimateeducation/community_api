import os
import time
from requests.adapters import HTTPAdapter
from requests_toolbelt import sessions
from .swc_token import CommunityToken


class SWCAdapter(HTTPAdapter):
    """A Custom HTTPAdapter for interacting with SWC
    - Automatically set and refresh the JWT Token
    - Throttle calls to the API endpoint to be within throttle limits
    - Always set a default timeout
    """

    DEFAULT_TIMEOUT = 60  # seconds
    SWC_API_RATE = 0.3

    def __init__(self, *args, swc_token, **kwargs):
        self.swc_token = swc_token
        self.token, self.token_exp = self.swc_token.get_token()
        self.timeout = self.DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def add_headers(self, r, **kwargs):
        """Attach an API token to a custom auth header."""
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        self.handle_token()
        return super().send(request, **kwargs)

    def handle_token(self):
        """Reset the SWC JWT when we get close to or pass expiration"""
        now = int(time.time())
        # if we're within 10 seconds of the JWT expiring refresh it
        if now >= self.token_exp - 20:
            self.token, self.token_exp = self.swc_token.get_token()

    def build_response(self, req, resp):
        # throttle calls
        time.sleep(self.SWC_API_RATE)
        return super().build_response(req, resp)


class SWCSession(sessions.BaseUrlSession):
    """Custom Requests session for interacting with SWC
    - Always set the max row limit for GET requests
    - Provide a get_all method for paginating a GET request
    """

    SWC_ROW_LIMIT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(kwargs.get("base_url"))

    def get_all(self, url, **kwargs):
        """Add pagination to basic get request """
        response = self.get(url, **kwargs)
        data = response.json()

        while self.has_more_pages(response):
            next_page = response.links.get("next").get("url")
            response = self.get(next_page)
            data += response.json()

        return data

    def all_records(self, url, **kwargs):
        """Paginate and yield each record as a generator """
        response = self.get(url, **kwargs)
        for r in response.json():
            yield r

        while self.has_more_pages(response):
            next_page = response.links.get("next").get("url")
            response = self.get(next_page)
            for r in response.json():
                yield r

    def has_more_pages(self, response):
        """Check headers to see if this response has more pages """
        return (
            response
            and response.links
            and response.links.get("next").get("rel") == "next"
        )

    def get(self, url, **kwargs):
        """Override get to add the max page size limit by default """
        params = kwargs.get("params", {})
        if "limit" not in params:
            params["limit"] = self.SWC_ROW_LIMIT
        kwargs["params"] = params
        return super().get(url, **kwargs)


def swc_connection(
    community_domain=os.getenv("SWC_AUDIENCE"),
    app_id=os.getenv("SWC_APP_ID"),
    app_secret=os.getenv("SWC_SECRET"),
    user_id=os.getenv("SWC_USER_ID"),
    swc_token=None,
):
    """Return an instrumented requests session for interacting with SWC

    Both the JWT Token generator and community_domain will use environmental variables to initialize if not provided
    here

    :param community_domain: The FQDN of the Community instance being connected to
    :param swc_token: The CommunityToken class to use to generate JWT tokens
    """
    base_url = f"https://{community_domain}/services/4.0/"
    # use the passed in token provider otherwise create one with OAuth variables
    token_provider = swc_token or CommunityToken(
        community_domain=community_domain,
        app_id=app_id,
        app_secret=app_secret,
        user_id=user_id,
    )
    http = SWCSession(base_url=base_url)
    http.mount(base_url, SWCAdapter(swc_token=token_provider))
    # always raise and error for failed calls
    assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
    http.hooks["response"] = [assert_status_hook]
    return http
