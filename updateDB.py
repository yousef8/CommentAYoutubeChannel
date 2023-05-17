from oauth import get_credentials
from database import Playlist
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys
import json

import logging
import logging.handlers

###################### Logger configurations #############################
logger = logging.getLogger("updateDB")
logger.setLevel(logging.DEBUG)

styleFormat = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s", datefmt="%d-%m-%Y %H:%M:%S")

fileHandler = logging.handlers.TimedRotatingFileHandler(
    filename="logger.log", when="w5")

fileHandler.setFormatter(styleFormat)

fileHandler.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)


########################## Main code ################################

def update_db(id):

    logger.info("Getting Credentials")
    credentials = get_credentials()
    logger.info("Credentials acquired")

    # 1 - check if table for this playlist exists or not
    channel = Playlist(id.replace('-', ''))

    # 2 - get existing videos count
    existing_videos_count = channel.get_total_videos_count()
    logger.info(f"There are {existing_videos_count} existing videos")

    # 3 - videos count on the from youtube
    updated_videos_count = 0
    with build('youtube', 'v3', credentials=credentials) as youtube:

        request = youtube.playlists().list(
            part='contentDetails',
            id=id
        )

        # Didn't know how get the status code of the response so had to make a workaround if wrong channelId then the 'items' list
        # will be empty and will result in this error
        try:
            res = request.execute()
            updated_videos_count = res['items'][0]['contentDetails']['itemCount']
        except IndexError:
            logger.error("Wrong Channel ID")
            return

        logger.info(
            f"There are {updated_videos_count} videos on the channel online")

    # 4 - how many videos need to get added to DB
    new_videos_count = updated_videos_count - existing_videos_count
    logger.info(f"There are {new_videos_count} new videos")

    # 5 - Fetch and Add them to DB
    if 0 < new_videos_count <= 50:
        with build('youtube', 'v3', credentials=credentials) as youtube:
            request = youtube.playlistItems().list(part="snippet", maxResults=new_videos_count, playlistId=id,
                                                   fields="items/snippet(title,resourceId/videoId),pageInfo")
            res = request.execute()
            for video in res['items']:
                channel.add_video(video['snippet']['title'],
                                  video['snippet']['resourceId']['videoId'])
                logger.info(
                    f"Video with title [{video['snippet']['title']}] Added to DB")
            logger.info("Removing Duplicates")
            channel.remove_duplicates()

    if new_videos_count > 50:
        with build('youtube', 'v3', credentials=credentials) as youtube:
            next_page_token = None
            for i in range(new_videos_count//50 + bool(new_videos_count % 50)):
                request = youtube.playlistItems().list(part="snippet", maxResults=50, playlistId=id,
                                                       fields="nextPageToken,items/snippet(title,resourceId/videoId),pageInfo", pageToken=next_page_token)
                res = request.execute()

                if 'nextPageToken' in res:
                    next_page_token = res['nextPageToken']

                for video in res['items']:
                    channel.add_video(video['snippet']['title'],
                                      video['snippet']['resourceId']['videoId'])
                    logger.info(
                        f"Video with title [{video['snippet']['title']}] Added to DB")
                logger.info("Removing Duplicates")
                channel.remove_duplicates()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        logger.info("Missing Channel ID argument!!!")
    else:
        update_db(sys.argv[1])
