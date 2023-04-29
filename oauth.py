from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from oauthlib.oauth2.rfc6749.errors import AccessDeniedError
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError


def start_oauth():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],)

    print("Start Oauth Process...")

    try:
        flow.run_local_server(prompt="consent")
    except AccessDeniedError:
        print("Access Denied")
        return None

    try:
        credentials = flow.credentials
    except ValueError:
        print("There was no access token adquired")
        print("Run the script again for another try")
        return None

    print("Tokens Acquired")
    print("Saving Tokens")
    with open("tokens.json", "w") as f:
        f.write(credentials.to_json())
        print("Credentiasl Saved")

    return credentials


def get_credentials():
    try:
        print("Loading saved tokens")
        credentials = Credentials.from_authorized_user_file("tokens.json")
        print("Tokens acquired successfully")
    except FileNotFoundError:
        print("There is no saved tokens")
        return start_oauth()

    print("Checking tokens Validity")
    if credentials.valid:
        print("Tokens are valid")
        return credentials

    if credentials.expired and credentials.refresh_token:
        print("Token is expired")
        try:
            print("Regreshing token")
            credentials.refresh(Request())
            print("Token refreshed successfully")
        except RefreshError:
            print("Couldn't refresh tokens")
            return None

        print("Saving tokens")
        with open("tokens.json", "w") as f:
            f.write(credentials.to_json())
            print("Saved successfully")

        return credentials
    return start_oauth()


get_credentials()
