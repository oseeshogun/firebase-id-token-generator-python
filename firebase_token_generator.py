import argparse
import json, os
from urllib import parse, request

import firebase_admin
from firebase_admin import credentials, auth

from dotenv import load_dotenv

load_dotenv()

# Configuration ================================================================
DATABASE_URL = os.getenv('DATABASE_URL')
# Download from
# Firebase Console > Settings > Service Accounts > Generate New Private key
PATH_TO_PRIVATE_KEY = "key.json"
# Copy from
# Firebase Console > Settings > General > Web API Key
API_KEY = os.getenv('API_KEY')
# ==============================================================================

cred = credentials.Certificate(PATH_TO_PRIVATE_KEY)
default_app = firebase_admin.initialize_app(
    cred, {"databaseURL": DATABASE_URL})


def get_token(uid):
    """Return a Firebase ID token dict from a user id (UID).

    Returns:
      dict: Keys are "kind", "idToken", "refreshToken", and "expiresIn".
      "expiresIn" is in seconds.

      The return dict matches the response payload described in
      https://firebase.google.com/docs/reference/rest/auth/#section-verify-custom-token

      The actual token is at get_token(uid)["idToken"].

    """
    token = auth.create_custom_token(uid)
    data = parse.urlencode({
        'token': token,
        'returnSecureToken': True
    }).encode()

    url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty" \
          "/verifyCustomToken?key={}".format(API_KEY)

    req = request.Request(url,
                                 data=data)
    response = request.urlopen(req).read()

    return json.loads(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Firebase ID token "
                                                 "from a user id (UID).")
    parser.add_argument("uid", help="Firebase User ID (UID)", type=str)
    args = parser.parse_args()

    print(get_token(args.uid)["idToken"])
