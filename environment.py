import os
from dotenv import load_dotenv

load_dotenv("./music_web_page.env")


class Environment:
    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecret")
        self.DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///music.db")
        self.APP_NAME = os.getenv("APP_NAME", "MusicApp")
        self.APP_DEBUG_MODE_ENABLE = os.getenv("APP_DEBUG_MODE_ENABLE", "False").lower() in ("true", "1", "yes")
        self.APP_UPLOAD_FOLDER = os.getenv("APP_UPLOAD_FOLDER", "static")
        self.ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
        self.ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "super")
        self.ADMIN_APP_TEMPLATE_MODE = os.getenv("ADMIN_APP_TEMPLATE_MODE", "bootstrap4")
        self.ADMIN_APP_NAME = os.getenv("ADMIN_APP_NAME", "Music Admin")
        self.ADMIN_APP_PROFILE_VIEW_NAME = os.getenv("ADMIN_APP_PROFILE_VIEW_NAME", "Profile")
        self.ADMIN_APP_TOUR_VIEW_NAME = os.getenv("ADMIN_APP_TOUR_VIEW_NAME", "Tour")
        self.ADMIN_APP_CONCERT_VIEW_NAME = os.getenv("ADMIN_APP_CONCERT_VIEW_NAME", "Concert")
        self.ADMIN_APP_PLACE_VIEW_NAME = os.getenv("ADMIN_APP_PLACE_VIEW_NAME", "Place")
        self.ADMIN_APP_ADDRESS_VIEW_NAME = os.getenv("ADMIN_APP_ADDRESS_VIEW_NAME", "Address")
        self.ADMIN_APP_ALBUM_VIEW_NAME = os.getenv("ADMIN_APP_ALBUM_VIEW_NAME", "Album")
        self.ADMIN_APP_BOARD_MESSAGE_VIEW_NAME = os.getenv("ADMIN_APP_BOARD_MESSAGE_VIEW_NAME", "Board Message")

        self.ADMIN_APP_PAGE_DESCRIPTION_VIEW_NAME = os.getenv("ADMIN_APP_PAGE_DESCRIPTION_VIEW_NAME", "Page Description")

        self.APP_WSGI_MODE_ENABLE = os.getenv("APP_WSGI_MODE_ENABLE", "False").lower() in ("true", "1", "yes")
        

        year = os.getenv("APP_LICENSE_YEAR", "Unknown Year")
        owner = os.getenv("APP_LICENSE_OWNER", "Unknown Owner")
        phrase = os.getenv("APP_LICENSE_TEXT", "All rights reserved")
        self.APP_LICENSE = f"{year} {owner} {phrase}" 

env = Environment()
