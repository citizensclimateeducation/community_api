import os
import time
import requests
import json
from authlib.jose import JsonWebSignature

SWC_SCOPE = "create delete read update"
JWT_TOKEN_HEADER = {"alg": "HS256"}
TOKEN_DURATION = 120


class CommunityToken:
    def __init__(
        self,
        community_domain=os.getenv("SWC_AUDIENCE"),
        app_id=os.getenv("SWC_APP_ID"),
        app_secret=os.getenv("SWC_SECRET"),
        user_id=os.getenv("SWC_USER_ID"),
    ):
        self.community_domain = community_domain
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_id = user_id

    def get_token(self):
        """Return a JWT token and expiration time for making API calls to Small World Community

        Arguments to this function will, by default, use environmental variables if they are present (noted below)

        :param community_domain: the FQDN of the community instance (SWC_AUDIENCE)
        :param app_id: the the Oauth Application ID being used to connect to the community API (SWC_APP_ID)
        :param user_id: The SWC User ID of the authorized user attached to this Oauth Application (SWC_USER_ID)
        :return: A tuple with token to use with request calls and the time (in seconds) when the token will expire
        """
        exp = int(time.time()) + TOKEN_DURATION
        payload = {
            "iss": self.app_id,
            "iat": int(time.time()),
            "aud": self.community_domain,
            "exp": exp,
            "sub": self.user_id,
            "scope": SWC_SCOPE,
        }
        jws = JsonWebSignature(["HS256"])
        auth_token = jws.serialize_compact(
            JWT_TOKEN_HEADER,
            bytearray(json.dumps(payload), "utf-8"),
            bytearray(self.app_secret, "utf-8"),
        )
        swc_token_url = f"https://{self.community_domain}/services/4.0/token"
        token_request = requests.post(
            swc_token_url,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": auth_token.decode("utf-8"),
                "content_type": "application/x-www-form-urlencoded",
            },
        )
        token_request.raise_for_status()
        token = token_request.json().get("access_token")
        return token, exp
