import sqlite3


class Playlist:
    def __init__(self, playlist_id):
        # Sanitize Input
        self.playlist_id = playlist_id.replace('-', '')
        self.connection = sqlite3.connect("videos.db")
        self.cur = self.connection.cursor()
        self.create_table()

    def __del__(self):
        self.connection.close()

    def create_table(self):
        self.cur.execute(
            f"CREATE TABLE IF NOT EXISTS {self.playlist_id} (title text, link text, videoID text NOT NULL, commented text DEFAULT NO)")
        self.connection.commit()

    def get_total_videos_count(self):
        self.cur.execute(f"SELECT COUNT(*) FROM {self.playlist_id}")
        return self.cur.fetchone()[0]

    def add_video(self, title, video_id, is_commented="NO"):
        # Sanitize the title input
        title = title.replace("'", "")
        self.cur.execute(
            f"INSERT INTO {self.playlist_id} (title, link, videoID, commented) VALUES ('{title}', '{'https://www.youtube.com/watch?v='+video_id}', '{video_id}', '{is_commented}')")
        self.connection.commit()

    def mark_commented(self, video_id):
        self.cur.execute(
            f"UPDATE {self.playlist_id} SET commented = 'YES' WHERE videoID = '{video_id}'"
        )
        self.connection.commit()
        print(self.cur.fetchall())

    def get_next_uncommented_video(self):
        '''Returns dict{title, link, id, commented}'''
        self.cur.execute(
            f"SELECT *  FROM {self.playlist_id} WHERE commented = 'NO' LIMIT 1"
        )
        self.connection.commit()
        video = self.cur.fetchone()

        return {'title': video[0], 'link': video[1], 'id': video[2], 'commented': video[3]}

    def remove_duplicates(self):
        self.cur.execute(
            f"DELETE FROM {self.playlist_id} WHERE rowid NOT IN (SELECT rowid FROM {self.playlist_id} GROUP BY videoID)"
        )
        self.connection.commit()
