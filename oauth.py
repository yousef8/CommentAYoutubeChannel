from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from oauthlib.oauth2.rfc6749.errors import AccessDeniedError
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import logging
import logging.handlers

###################### Logger configurations #############################
logger = logging.getLogger("oauth")
logger.setLevel(logging.DEBUG)

styleFormat = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s", datefmt="%d-%m-%Y %H:%M:%S")

fileHandler = logging.handlers.TimedRotatingFileHandler(
    filename="logger.log", when="w5")

fileHandler.setFormatter(styleFormat)

fileHandler.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)


########################## Main code ################################

def start_oauth():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.force-ssl"],)

    logger.info("Start Oauth Process...")

    try:
        flow.run_local_server(prompt="consent")
    except AccessDeniedError:
        logger.info("Access Denied")
        return None

    try:
        credentials = flow.credentials
    except ValueError:
        logger.info("There was no access token adquired")
        logger.info("Run the script again for another try")
        return None

    logger.info("Tokens Acquired")
    logger.info("Saving Tokens")
    with open("tokens.json", "w") as f:
        f.write(credentials.to_json())
        logger.info("Credentiasl Saved")

    return credentials


def get_credentials():
    try:
        logger.info("Loading saved tokens")
        credentials = Credentials.from_authorized_user_file("tokens.json")
        logger.info("Tokens acquired successfully")
    except FileNotFoundError:
        logger.info("There is no saved tokens")
        return start_oauth()

    logger.info("Checking tokens Validity")
    if credentials.valid:
        logger.info("Tokens are valid")
        return credentials

    if credentials.expired and credentials.refresh_token:
        logger.info("Token is expired")
        try:
            logger.info("Regreshing token")
            credentials.refresh(Request())
            logger.info("Token refreshed successfully")

            logger.info("Saving tokens")
            with open("tokens.json", "w") as f:
                f.write(credentials.to_json())
                logger.info("Saved successfully")

            return credentials
        except RefreshError:
            logger.info("Couldn't refresh tokens")
            return None

    return start_oauth()
