


from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask import request

from auth import AdminAuthenticator
from database import Album, BoardMessage, PageDescription, Profile, Tour


class AdminView(ModelView):
    can_export = True
    create_modal = True
    edit_modal = True
    page_size = 50

    def __init__(self, model, session, admin_authenticator: AdminAuthenticator, **kwargs):
        super().__init__(model, session, **kwargs)
        self.admin_authenticator = admin_authenticator  # istanza di AdminAuthenticator

    def is_accessible(self):
        auth = request.authorization
        return auth and self.admin_authenticator.check_auth(auth.username, auth.password)

    def inaccessible_callback(self, name, **kwargs):
        return self.admin_authenticator.authenticate()


# --- Admin Index ---

class AppAdminIndexView(AdminIndexView):
    def __init__(self, admin_authenticator: AdminAuthenticator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_authenticator = admin_authenticator

    def is_accessible(self):
        auth = request.authorization
        return (
            auth and
            self.admin_authenticator.check_auth(username=auth.username, password=auth.password)
        )

    def inaccessible_callback(self, name, **kwargs):
        return self.admin_authenticator.authenticate()

    @expose('/')
    def index(self):
        profile = Profile.query.first()
        albums = Album.query.all()
        tours = Tour.query.all()
        board_messages = BoardMessage.query.order_by(BoardMessage.created_at.desc()).all()
        page_description = PageDescription.query.first()
        return self.render(
            'admin_index.html',
            profile=profile,
            albums=albums,
            tours=tours,
            board_messages=board_messages,
            page_description=page_description
        )
