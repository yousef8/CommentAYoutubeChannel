from oauth import get_credentials
from database import Playlist
from googleapiclient.discovery import build
import sys

import logging
import logging.handlers

###################### Logger configurations #############################
logger = logging.getLogger("updateDB")
logger.setLevel(logging.DEBUG)

styleFormat = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s", datefmt="%d-%m-%Y %H:%M:%S")

streamFormat = logging.Formatter("%(levelname)s - %(message)s")

fileHandler = logging.handlers.TimedRotatingFileHandler(
    filename="logger.log", when="w5")

streamHandler = logging.StreamHandler(stream=sys.stdout)

fileHandler.setFormatter(styleFormat)
streamHandler.setFormatter(streamFormat)

fileHandler.setLevel(logging.DEBUG)
streamHandler.setLevel(logging.DEBUG)

logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

########################## Main code ################################


def add_comment(channel_id, comment):
    # 1 - Get Credentails
    logger.info("Getting Credentials")

    try:

        credentials = get_credentials()

        if credentials == None:
            logger.critical("Can't Acquire Credentials")
            return
    except:
        logger.critical("Couldn't Acquire Credentials")
        return

    logger.info("Credentials Acquired")

    # 2 - Get the video ID
    pl = Playlist(channel_id)

    if pl.get_total_videos_count() == 0:
        logger.info('This playlist is not in DB')
        logger.info('Please run "updateDB.py <channelID>"')
        pl.remove_playlist()
        return

    try:
        video = pl.get_next_uncommented_video()
    except TypeError:
        logger.info('All videos in DB are commented')
        return

    # 3 - Add comment to video
    with build('youtube', 'v3', credentials=credentials) as youtube:
        req = youtube.commentThreads().insert(
            part="snippet",
            body={"snippet": {"videoId": video['id'], "topLevelComment": {
                "snippet": {"textOriginal": comment}}}}
        )
        res = req.execute()
        logger.info("Comment Added Successfully")
        pl.mark_commented(video['id'])
        logger.info("Updated video comment status in DB")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Missing Channel ID")
    else:
        try:
            comment = ''
            with open('comment.txt', 'r') as f:
                comment = f.read()
        except:
            logger.critical("Couldn't open the comment file")
            sys.exit()

        add_comment(sys.argv[1], comment)
