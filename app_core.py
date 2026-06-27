from admin_base import AppAdminIndexView
from admin_views import AddressAdmin, AlbumAdmin, BoardMessageAdmin, ConcertAdmin, PageDescriptionAdmin, PlaceAdmin, ProfileAdmin, TourAdmin
from auth import AdminAuthenticator

from flask import ( 
    Flask, render_template, abort
)

from flask_admin import Admin
from flask_babel import Babel

from environment import env
from database import ( db, Tour, Concert, Place, Address, Profile, Album, BoardMessage, PageDescription )
from cookie_support import CookieSupporter



class App:
    app_default_name = "Music Web App"
    app_default_debug_mode = False
    app_default_wsgi_mode = False
    app_default_db_uri = "sqlite:///music.db"

    admin_app_default_name = "Music Admin"
    admin_app_default_profile_view_name = "Profile"
    admin_app_default_tour_view_name = "Tour"
    admin_app_default_concert_view_name = "Concert"
    admin_app_default_place_view_name = "Place"
    admin_app_default_address_view_name = "Address"
    admin_app_default_album_view_name = "Album"
    admin_app_default_board_message_view_name = "Board Message"
    admin_app_default_page_description_view_name = "Page Descritpion"
    admin_app_template_modes = ['bootstrap2', 'bootstrap3', 'bootstrap4', 'bootstrap5', 'bootstrap5-v2']
    admin_app_default_template_mode = "bootstrap4"
    

    @staticmethod
    def create_app():
        app = App()
        return app
    
    def __init__(self):
        self.secret_key = None
        self.database_uri = None
        self.app_name = None
        self.app_debug_mode = None
        self.app_upload_folder = None
        self.app_album_image_folder = None
        self.app_profile_image_folder = None
        self.app_icon_folder = None
        self.admin_template_mode = None
        self.admin_password = None
        self.admin_username = None
        self.admin_app_name = None
        self.admin_app_profile_view_name = None
        self.admin_app_tour_view_name = None
        self.admin_app_concert_view_name = None
        self.admin_app_place_view_name = None
        self.admin_app_address_view_name = None
        self.admin_app_album_view_name = None
        self.admin_app_board_message_view_name = None
        self.admin_app_page_descritpion_view_name = None
        self.app_wsgi_mode = None

        
    def get_flask_app(self):
        return self.app

    def register_routes(self):
        @self.app.route('/')
        def index():
            profile = Profile.query.first()
            if not profile:
                abort(404, description="Page Not Found")

            albums = Album.query.all()
            tours = Tour.query.all()
            board_messages = BoardMessage.query.order_by(BoardMessage.created_at.desc()).all()
            page_description = PageDescription.query.first()
            essential_cookie = self.cookie_supporter.get_essential()
            not_essential_cookie = self.cookie_supporter.get_not_essential()
            app_license = self.app_license
            return render_template(
                'index.html',
                profile=profile,
                albums=albums,
                tours=tours,
                board_messages=board_messages,
                page_description=page_description,
                app_license=app_license,
                essential_cookie=essential_cookie,
                not_essential_cookie=not_essential_cookie
            )

    def start(self):
        self.app.run(port=8000, debug=self.app_debug_mode)

    def get_config(self, attribute: str = None):
        return self.app.config[attribute] if attribute else self.app.config 

    def configure(self):
        
        # App
        self.app_name = env.APP_NAME if 0 < len(str(env.APP_NAME)) < 64 else App.app_default_name
        self.app = Flask(self.app_name)
        self.babel = Babel(self.app)
        self.app_debug_mode = env.APP_DEBUG_MODE_ENABLE if env.APP_DEBUG_MODE_ENABLE in [True, False] else App.app_default_debug_mode
        self.app_wsgi_mode = env.APP_WSGI_MODE_ENABLE if env.APP_WSGI_MODE_ENABLE in [True, False] else App.app_default_wsgi_mode
        self.app_upload_folder = env.APP_UPLOAD_FOLDER
        self.app_album_image_folder = f"{self.app_upload_folder}/images/album"
        self.app_profile_image_folder = f"{self.app_upload_folder}/images/profile"
        self.app_icon_folder = f"{self.app_upload_folder}/icons"
        self.app_license = env.APP_LICENSE
        self.app.config['APP_NAME'] = self.app_name
        self.app.config['APP_DEBUG_MODE_ENABLE'] = self.app_debug_mode
        self.app.config['APP_WSGI_MODE_ENABLE'] = self.app_wsgi_mode
        self.app.config['APP_UPLOAD_FOLDER'] = self.app_upload_folder
        self.app.config['APP_ALBUM_IMAGE_FOLDER'] = self.app_album_image_folder
        self.app.config['APP_PROFILE_IMAGE_FOLDER'] = self.app_profile_image_folder
        self.app.config['APP_ICON_FOLDER'] = self.app_icon_folder
        self.app.config['APP_LICENSE'] = self.app_license


        # Database
        self.database_uri = env.DATABASE_URI if env.DATABASE_URI.startswith("sqlite://") and env.DATABASE_URI.endswith(".db") else App.app_default_db_uri
        self.secret_key = env.SECRET_KEY
        self.app.config['SECRET_KEY'] = self.secret_key
        self.app.config['SQLALCHEMY_DATABASE_URI'] = self.database_uri
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        

        # Admin
        self.admin_username = env.ADMIN_USERNAME
        self.admin_password = env.ADMIN_PASSWORD
        self.app.config['ADMIN_USERNAME'] = self.admin_username
        self.app.config['ADMIN_PASSWORD'] = self.admin_password
        self.admin_app_template_mode = env.ADMIN_APP_TEMPLATE_MODE if env.ADMIN_APP_TEMPLATE_MODE in App.admin_app_template_modes else App.admin_app_default_template_mode
        self.admin_app_name = env.ADMIN_APP_NAME if 0 < len(str(env.ADMIN_APP_NAME)) < 64 else App.admin_app_default_name
        self.admin_app_profile_view_name = env.ADMIN_APP_PROFILE_VIEW_NAME if 0 < len(str(env.ADMIN_APP_PROFILE_VIEW_NAME)) < 64 else App.admin_app_default_profile_view_name
        self.admin_app_tour_view_name = env.ADMIN_APP_TOUR_VIEW_NAME if 0 < len(str(env.ADMIN_APP_TOUR_VIEW_NAME)) < 64 else App.admin_app_default_tour_view_name
        self.admin_app_concert_view_name = env.ADMIN_APP_CONCERT_VIEW_NAME if 0 < len(str(env.ADMIN_APP_CONCERT_VIEW_NAME)) < 64 else App.admin_app_default_concert_view_name
        self.admin_app_place_view_name = env.ADMIN_APP_PLACE_VIEW_NAME if 0 < len(str(env.ADMIN_APP_PLACE_VIEW_NAME)) < 64 else App.admin_app_default_place_view_name
        self.admin_app_address_view_name = env.ADMIN_APP_ADDRESS_VIEW_NAME if 0 < len(str(env.ADMIN_APP_ADDRESS_VIEW_NAME)) < 64 else App.admin_app_default_address_view_name
        self.admin_app_album_view_name = env.ADMIN_APP_ALBUM_VIEW_NAME if 0 < len(str(env.ADMIN_APP_ALBUM_VIEW_NAME)) < 64 else App.admin_app_default_album_view_name
        self.admin_app_board_message_view_name = env.ADMIN_APP_BOARD_MESSAGE_VIEW_NAME if 0 < len(str(env.ADMIN_APP_BOARD_MESSAGE_VIEW_NAME)) < 64 else App.admin_app_default_board_message_view_name
        self.admin_app_page_description_view_name = env.ADMIN_APP_PAGE_DESCRIPTION_VIEW_NAME if 0 < len(str(env.ADMIN_APP_PAGE_DESCRIPTION_VIEW_NAME)) < 64 else App.admin_app_default_page_description_view_name
        self.app.config['ADMIN_TEMPLATE_MODE'] = self.admin_app_template_mode
        self.app.config['ADMIN_APP_NAME'] = self.admin_app_name
        self.app.config['ADMIN_APP_PROFILE_VIEW_NAME'] = self.admin_app_profile_view_name
        self.app.config['ADMIN_APP_TOUR_VIEW_NAME'] = self.admin_app_tour_view_name
        self.app.config['ADMIN_APP_CONCERT_VIEW_NAME'] = self.admin_app_concert_view_name
        self.app.config['ADMIN_APP_PLACE_VIEW_NAME'] = self.admin_app_place_view_name
        self.app.config['ADMIN_APP_ADDRESS_VIEW_NAME'] = self.admin_app_address_view_name
        self.app.config['ADMIN_APP_ALBUM_VIEW_NAME'] = self.admin_app_album_view_name
        self.app.config['ADMIN_APP_BOARD_MESSAGE_VIEW_NAME'] = self.admin_app_board_message_view_name
        self.app.config['ADMIN_APP_PAGE_DESCRIPTION_VIEW_NAME'] = self.admin_app_page_description_view_name
        
        return self.app.config


        

    def init(self):
        
        self.cookie_supporter = CookieSupporter(self.app)
        self.error_handler = ErrorHandler(self.app)
        self.register_routes()

        self.admin_authenticator = AdminAuthenticator(self.admin_username, self.admin_password)

        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()


        self.admin = Admin(
            self.app,
            name=self.admin_app_name,
            template_mode=self.admin_template_mode,
            index_view=AppAdminIndexView(self.admin_authenticator)
        )

        self.admin.add_view(ProfileAdmin(Profile, db.session, admin_authenticator=self.admin_authenticator, app=self, name=self.admin_app_profile_view_name))
        self.admin.add_view(AlbumAdmin(Album, db.session, admin_authenticator=self.admin_authenticator, app=self, name=self.admin_app_album_view_name))
        self.admin.add_view(BoardMessageAdmin(BoardMessage, db.session, admin_authenticator=self.admin_authenticator, app=self, name=self.admin_app_board_message_view_name))
        self.admin.add_view(PageDescriptionAdmin(PageDescription, db.session, admin_authenticator=self.admin_authenticator, app=self, name=self.admin_app_page_descritpion_view_name))  # Se non hai parametro in .env, lasci statico
        self.admin.add_view(AddressAdmin(Address, db.session, admin_authenticator=self.admin_authenticator, app=self, name=self.admin_app_address_view_name))
        self.admin.add_view(PlaceAdmin(Place, db.session, admin_authenticator=self.admin_authenticator, app=self, name=self.admin_app_place_view_name))
        self.admin.add_view(ConcertAdmin(Concert, db.session, admin_authenticator=self.admin_authenticator, app=self, name=self.admin_app_concert_view_name))
        self.admin.add_view(TourAdmin(Tour, db.session, admin_authenticator=self.admin_authenticator, app=self, name=self.admin_app_tour_view_name))
        



class ErrorHandler:
    def __init__(self, app):
        self.app = app
        self.register_routes()

    def register_routes(self):
        @self.app.errorhandler(404)
        def page_not_found(e):
            return render_template('404.html', message=e.description), 404

        @self.app.route("/social_not_found")
        def social_not_found():
            return render_template("404.html", message="Nessun link social trovato."), 404

        @self.app.route("/music_channel_not_found")
        def music_channel_not_found():
            return render_template("404.html", message="Nessun link a music channel trovato."), 404

        @self.app.route("/phone_not_found")
        def phone_not_found():
            return render_template("404.html", message="Nessun phone trovato."), 404

        @self.app.route("/email_not_found")
        def email_not_found():
            return render_template("404.html", message="Nessun contatto email trovato."), 404