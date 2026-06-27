from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app_core import App


from datetime import datetime
from markupsafe import Markup
import os
from werkzeug.utils import secure_filename
from wtforms.validators import DataRequired, ValidationError
from wtforms.widgets import FileInput
from markupsafe import Markup

from flask import ( 
   flash, request, url_for
)


from flask_admin.form.upload import ImageUploadField
from flask_admin.form import rules
from flask_admin.form import Select2Widget

from admin_base import AdminView




from auth import AdminAuthenticator
from database import (
    Album, BoardMessage, ConcertSchedule, PageDescription, Tour, TourSchedule, db, Concert, Place, Address, Ticket,
    MusicChannels, Socials, Profile, Contact
)

from wtforms import (
    FileField, TextAreaField, DateField, FormField, ValidationError, SelectMultipleField
)

from forms import ConcertScheduleForm, ProfileForm, TicketForm
from validators import FormValidators



from flask_admin import BaseView, expose

class PreviewView(BaseView):
    def __init__(self, name="Preview", endpoint="preview", **kwargs):
        super().__init__(name=name, endpoint=endpoint, **kwargs)

    @expose('/')
    def preview(self, **kwargs):
        profile = Profile.query.first()
        albums = Album.query.all()
        tours = Tour.query.all()
        board_messages = BoardMessage.query.order_by(BoardMessage.created_at.desc()).all()
        page_description = PageDescription.query.first()
        return self.render(
            'admin/preview.html',
            profile=profile,
            albums=albums,
            tours=tours,
            board_messages=board_messages,
            page_description=page_description
        )
    
class ProfileAdmin(AdminView):
    form_base_class = ProfileForm
    column_list = (
        "name", "bio", "profile_image",
        "contact.email", "contact.phone",
        "music_channels.spotify_link", "music_channels.youtube_link", "music_channels.applemusic_link",
        "socials.facebook_link", "socials.instagram_link"
    )
    form_overrides = dict(profile_image=FileField)
    

    # Creazione widget per immagine
    def _image_formatter(self, view, context, model, name):
        filename = getattr(model, name)
        if filename:
            relative_path = f'images/profile/{filename}'
            url = url_for(self.app.app_upload_folder, filename=relative_path)
            print("url "+str(url))
            return Markup(f'<img src="{url}" style="height:80px;">')
        return ""

    def __init__(self, model, session, admin_authenticator: AdminAuthenticator, app, **kwargs):
        self.app = app
        self.column_formatters = {
            'profile_image': self._image_formatter,
            'bio': lambda v, c, m, p: (str(m.bio)[:100] + '...') if m.bio and len(m.bio) > 10 else (str(m.bio) if m.bio else 'No Bio')
        }

        # Escludiamo le colonne relazionate che non vogliamo come oggetti
        self.form_excluded_columns = ['contact', 'music_channels', 'socials']

        super().__init__(model, session, admin_authenticator, **kwargs)
        
    def scaffold_form(self):
        
        form_class = super().scaffold_form()

        print("app_profile_image_folder scaffold " + self.app.app_profile_image_folder)
        form_class.profile_image = ImageUploadField(
            'Profile Image',
            base_path=self.app.app_profile_image_folder,
            url_relative_path='images/profile/',
            thumbnail_size=(150, 150, True)
        )
        return form_class


    def _ensure_relation(self, model, attr_name, relation_cls):
        rel = getattr(model, attr_name)
        if rel is None:
            rel = relation_cls()
            setattr(model, attr_name, rel)
            db.session.add(rel)
        return rel
    
    def on_form_prefill(self, form, id):
        profile = Profile.query.get(id)

        if profile.profile_image:
            form._existing_profile_image = profile.profile_image

        if profile.contact:
            form.email.data = profile.contact.email
            form.phone.data = profile.contact.phone

        if profile.music_channels:
            form.spotify_link.data = profile.music_channels.spotify_link
            form.youtube_link.data = profile.music_channels.youtube_link
            form.applemusic_link.data = profile.music_channels.applemusic_link

        if profile.socials:
            form.facebook_link.data = profile.socials.facebook_link
            form.instagram_link.data = profile.socials.instagram_link

    def create_model(self, form):
        try:
            model = Profile()
            model.name = form.name.data
            model.bio = form.bio.data

            print("form.profile_image.data.filename " + str(form.profile_image.data.filename))
            print("profile image folder " + str(self.app.app_profile_image_folder))
            print("form.profile_image.data " + str(form.profile_image.data))
            # Gestione upload immagine (solo se l’utente carica un file)
            if form.profile_image.data:
                # FileStorage
                file_data = form.profile_image.data
                filename = secure_filename(file_data.filename)
                
                # Percorso assoluto
                upload_folder = os.path.join(os.getcwd(), self.app.app_profile_image_folder)
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                
                # Salvataggio corretto
                file_data.stream.seek(0)  # assicura che il file sia al principio
                file_data.save(filepath)
                
                # Salva solo il nome nel DB
                model.profile_image = filename

            else:
                # Nessun file caricato → lascia profile_image a None
                model.profile_image = None

            # Contact
            if form.email.data or form.phone.data:
                model.contact = Contact(email=form.email.data or None, phone=form.phone.data or None)
                db.session.add(model.contact)

            # Music channels
            if form.spotify_link.data or form.youtube_link.data or form.applemusic_link.data:
                model.music_channels = MusicChannels(
                    spotify_link=form.spotify_link.data or None,
                    youtube_link=form.youtube_link.data or None,
                    applemusic_link=form.applemusic_link.data or None
                )
                db.session.add(model.music_channels)

            # Socials
            if form.facebook_link.data or form.instagram_link.data:
                model.socials = Socials(
                    facebook_link=form.facebook_link.data or None,
                    instagram_link=form.instagram_link.data or None
                )
                db.session.add(model.socials)

            db.session.add(model)
            db.session.commit()
            flash("Profile created successfully", "success")
            return True
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating profile: {e}", "error")
            raise

    def update_model(self, form, model):
        try:
            model.name = form.name.data
            model.bio = form.bio.data

            file_data = form.profile_image.data
            if file_data and hasattr(file_data, 'filename') and file_data.filename != '':
                print("NUOVO file caricato")
                filename = secure_filename(file_data.filename)
                print(filename)
                upload_folder = os.path.join(os.getcwd(), self.app.app_profile_image_folder)
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                print(upload_folder)
                print(filepath)
                # Reset stream e salva
                file_data.stream.seek(0)
                file_data.save(filepath)

                # Salva solo il nome file nel modello
                model.profile_image = filename

            # Contact
            if form.email.data or form.phone.data:
                contact = self._ensure_relation(model, "contact", Contact)
                contact.email = form.email.data or None
                contact.phone = form.phone.data or None
            elif getattr(model, "contact", None):
                db.session.delete(model.contact)
                model.contact = None

            # Music channels
            if form.spotify_link.data or form.youtube_link.data or form.applemusic_link.data:
                mc = self._ensure_relation(model, "music_channels", MusicChannels)
                mc.spotify_link = form.spotify_link.data or None
                mc.youtube_link = form.youtube_link.data or None
                mc.applemusic_link = form.applemusic_link.data or None
            elif getattr(model, "music_channels", None):
                db.session.delete(model.music_channels)
                model.music_channels = None

            # Socials
            if form.facebook_link.data or form.instagram_link.data:
                s = self._ensure_relation(model, "socials", Socials)
                s.facebook_link = form.facebook_link.data or None
                s.instagram_link = form.instagram_link.data or None
            elif getattr(model, "socials", None):
                db.session.delete(model.socials)
                model.socials = None

            db.session.add(model)
            db.session.commit()
            flash("Profile updated successfully", "success")
            return True
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {e}", "error")
            raise


        
# --- Album admin ---
class AlbumAdmin(AdminView):
    form_columns = ['name', 'description', 'cover_image', 'spotify_link', 'youtube_link', 'applemusic_link']

    def __init__(self, model, session, admin_authenticator: AdminAuthenticator, app, **kwargs):
        self.app = app
        super().__init__(model, session, admin_authenticator, **kwargs)
        

        self.column_formatters = {
            'cover_image': lambda v, c, m, p: Markup(
                f'<img src="/{self.app.app_album_image_folder}/{m.cover_image}" style="height:100px;">'
            ) if m.cover_image else ''
        }

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.cover_image = ImageUploadField(
            'Cover Image',
            base_path=self.app.app_album_image_folder,
            url_relative_path='images/album/',
            thumbnail_size=(150, 150, True)
        )
        return form_class

    def on_model_change(self, form, model, is_created):
        if model.name:
            FormValidators.validate_album_name(value=model.name, field_name="Name")
        
        if model.description:
            FormValidators.validate_album_description(value=model.description, field_name="Description")

        if model.spotify_link:
            FormValidators.validate_url(model.spotify_link, allowed_domains="spotify.com", field_name="Spotify Link")
        
        if model.youtube_link:
            FormValidators.validate_url(model.youtube_link, allowed_domains=["youtube.com", "youtu.be"], field_name="YouTube Link")
        
        if model.applemusic_link:
            FormValidators.validate_url(model.applemusic_link, allowed_domains="music.apple.com", field_name="Apple Music Link")

    def is_visible(self):
        return Profile.query.first() is not None




# --- BoardMessage admin ---
class BoardMessageAdmin(AdminView):
    column_list = ('content', 'created_at')
    form_columns = ('content',)
    form_overrides = {'content': TextAreaField}
    can_edit = True

    def __init__(self, model, session, admin_authenticator: AdminAuthenticator, app, **kwargs):
        self.app = app
        super().__init__(model, session, admin_authenticator, **kwargs)
        

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.created_at = datetime.utcnow()
        FormValidators.validate_board_message(value=model.content)

    def is_visible(self):
        return Profile.query.first() is not None


# --- PageDescription admin ---
class PageDescriptionAdmin(AdminView):
    column_list = ('content',)
    form_overrides = {'content': TextAreaField}

    def __init__(self, model, session, admin_authenticator: AdminAuthenticator, app, **kwargs):
        self.app = app
        super().__init__(model, session, admin_authenticator, **kwargs)

    def on_model_change(self, form, model, is_created):
        FormValidators.validate_page_description(value=model.content)
    
    def is_visible(self):
        return Profile.query.first() is not None






# --- Address Admin ---
class AddressAdmin(AdminView):
    column_list = ['id', 'country', 'region', 'province', 'cap', 'city', 'street', 'nr']
    form_columns = ['country', 'region', 'province', 'cap', 'city', 'street', 'nr']


    def __init__(self, model, session, admin_authenticator: AdminAuthenticator, app, **kwargs):
        self.app = app
        super().__init__(model, session, admin_authenticator, **kwargs)
        self.admin_authenticator = admin_authenticator


    def on_model_change(self, form, model, is_created):
        # Tutti i campi stringa senza HTML
        for field_name in ['country', 'region', 'province', 'city', 'street']:
            val = getattr(model, field_name)
            
            if val:
                if FormValidators.contains_html(value=val):
                    raise ValidationError(f"{field_name} cannot contain HTML")
                if FormValidators.contains_sql(value=val):
                    raise ValidationError(f"{field_name} cannot contain SQL")
                if len(val) < 0 or len(val) > 100:
                    raise ValidationError(f"Invalid {field_name} must be min 0 characters max 100 characters")
            else:
                raise ValidationError(f"{field_name} cannot be empty")
        
        if model.cap:
            if FormValidators.contains_html(value=model.cap):
                raise ValidationError(f"Cap cannot contain HTML")
            if FormValidators.contains_sql(value=model.cap):
                    raise ValidationError(f"CAP cannot contain SQL")
            if not FormValidators.validate_cap(model.cap):
                raise ValidationError(f"Invalid CAP")
        else:
             raise ValidationError("CAP cannot be empty")
        
        if model.nr:
            if FormValidators.contains_html(value=model.nr):
                raise ValidationError(f"Nr cannot contain HTML")
            if FormValidators.contains_sql(value=model.nr):
                    raise ValidationError(f"Nr cannot contain SQL")
            if not FormValidators.validate_nr(model.nr):
                raise ValidationError("Invalid Nr")
        else:
             raise ValidationError(f"Nr {model.nr} cannot be empty")

        
    def __str__(self):
        return f"{self.country}, {self.region}, {self.province}, {self.cap} {self.city}, {self.street} {self.nr}"
    
    def is_visible(self):
        return Profile.query.first() is not None


# --- Place Admin ---
class PlaceAdmin(AdminView):
    column_list = ['id', 'venue', 'maps_link', 'address']
    form_columns = ['venue', 'maps_link', 'address']

    form_args = {
        'address': {
            'query_factory': lambda: Address.query.all(),
            'allow_blank': True,
            'get_label': lambda addr: f"{addr.street} {addr.nr}, {addr.city}"  # Mostra via e città
        }
    }

    def __init__(self, model, session, admin_authenticator: AdminAuthenticator, app, **kwargs):
        self.app = app
        super().__init__(model, session, admin_authenticator, **kwargs)

    def on_model_change(self, form, model, is_created):
        if model.venue:
            if len(model.venue) < 0 or len(model.venue) > 100:
                raise ValidationError(f"Venue {model.venue} must be min 0 characters max 100 characters")
            if FormValidators.contains_html(value=model.venue):
                raise ValidationError(f"Venue cannot contain HTML or be empty")
            if FormValidators.contains_sql(value=model.venue):
                    raise ValidationError(f"Venue cannot contain SQL")
        else:
            raise ValidationError(f"Venue {model.venue} cannot be empty")
        
        if model.maps_link:
            if FormValidators.contains_html(value=model.maps_link):
                raise ValidationError(f"Maps Link {model.maps_link} cannot contain HTML")
            if FormValidators.contains_sql(value=model.maps_link):
                    raise ValidationError(f"Venue {model.maps_link} cannot contain SQL")
            FormValidators.validate_url(model.maps_link, allowed_domains="google.com", field_name="Google Maps Link")
        #else:
        #     raise ValidationError(f"Maps Link {model.maps_link} cannot be empty")
        
        if not model.address:
            raise ValidationError(f"Address {str(model.address)} cannot be empty")
        
    def __str__(self):
        return f"{self.venue}, {str(self.address)}"
    
    def is_visible(self):
        return Profile.query.first() is not None
            

# --- Concert Admin ---
class InlineFormWidget:

    def __call__(self, field, **kwargs):
        parts = ['<div class="inline-form">']
        for sub in field.form:
            parts.append(
                f'<div class="inline-subfield form-group">'
                f'  <label class="inline-label">{sub.label.text}</label>'
                f'  <div class="inline-control">{sub()}</div>'
                f'</div>'
            )
        parts.append('</div>')
        return Markup(''.join(parts))




class ConcertAdmin(AdminView):
    column_list = ['id', 'place', 'ticket', 'concert_schedule']

    form_columns = ['place', 'ticket', 'concert_schedule']
    form_extra_fields = {
        'ticket': FormField(TicketForm, widget=InlineFormWidget()),
        'concert_schedule': FormField(ConcertScheduleForm, widget=InlineFormWidget()),
    }

    form_create_rules = (
        'place',
        rules.HTML('<div style="height:20px"></div>'),
        'ticket',
        rules.HTML('<div style="height:20px"></div>'),          
        'concert_schedule',
        rules.HTML('<div style="height:100px"></div>'),         
        rules.HTML("""
            <style>
            /* container mini-form */
            .inline-form {
                display: flex;
                flex-wrap: wrap;
                gap: 12px 24px; /* vertical / horizontal gap */
                align-items: flex-start; /* allineiamo top di ogni subfield */
                margin-left: 6px;
            }

            /* wrapper dei singoli controlli */
            .inline-subfield {
                display: flex;
                flex-direction: row; /* orizzontale */
                align-items: center; /* centra verticalmente checkbox e input text */
                gap: 8px;
                margin-bottom: 8px;
            }

            /* label sopra i campi */
            .inline-subfield .inline-label {
                font-weight: 600;
                font-size: 1.00rem;
                margin-right: 30px; /* spazio tra label e controllo */
                margin-top: 20px; /* spazio tra label e controllo */   
            }

            /* input text / date / time */
            .ticket-link, .schedule-date, .schedule-starttime, .schedule-endtime {
                border-radius: 8px;
                padding: 6px 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.08);
                transition: box-shadow .2s ease;
                margin-right: 10px;
                margin-top: 20px; /* spazio tra label e controllo */
            }

            /* checkbox centrata */
            .ticket-isfree {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 12px;
                height: 12px;
                margin-right: 10px;
                margin-top: 20px; /* spazio tra label e controllo */
            }

            /* distanza tra le sezioni */
            .form-group.form-field { margin-bottom: 30px; }
            </style>
            """)
    )
    form_edit_rules = form_create_rules

    form_args = {
        'place': {
            'query_factory': lambda: Place.query.all(),
            'allow_blank': True,
            'get_label': 'venue'
        }
    }

    column_formatters = {
        'ticket': lambda v, c, m, p: str(m.ticket) if m.ticket is not None else 'No Ticket',
        'concert_schedule': lambda v, c, m, p: str(m.concert_schedule) if m.concert_schedule else 'No Schedule',
        'place': lambda v, c, m, p: str(m.place) if m.place else 'No Place'
    }

    def __init__(self, model, session, admin_authenticator: AdminAuthenticator, app, **kwargs):
        self.app = app
        super().__init__(model, session, admin_authenticator, **kwargs)
    
    def on_form_prefill(self, form, id=None):
        model = self.get_one(id)
        if model:
            if model.ticket is None:
                model.ticket = Ticket()
            if model.concert_schedule is None:
                model.concert_schedule = ConcertSchedule()

    def create_model(self, form):
        try:
            model = self.model()

            ticket_link = form.ticket.ticket_link.data
            print(ticket_link)
            if not ticket_link or ticket_link.strip() == "":
                ticket_link = None
            print(ticket_link)
            model.ticket = Ticket(
                ticket_link=ticket_link,
                is_free=form.ticket.is_free.data
            )
            model.concert_schedule = ConcertSchedule(
                date=form.concert_schedule.date.data,
                starttime=form.concert_schedule.starttime.data,
                endtime=form.concert_schedule.endtime.data
            )

            form.populate_obj(model)

            if not self.validate_model(model):
                self.session.rollback()
                flash("Fail to validate concert", "error")
                return False

            self.session.add(model)
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            flash(f"Fail to create concert: excpetion {str(e)} with traceback {str(e.__traceback__)}", "error")
            return False
        
        



    def update_model(self, form, model):
        try:
            ticket = Ticket.query.filter_by(
                ticket_link=form.ticket.ticket_link.data or None,
                is_free=form.ticket.is_free.data
            ).first()

            if not ticket:
                ticket_link = form.ticket.ticket_link.data
                if not ticket_link or ticket_link.strip() == "":
                    ticket_link = None
                ticket = Ticket(
                    ticket_link=ticket_link,
                    is_free=form.ticket.is_free.data
                )


            date = form.concert_schedule.date.data
            start = form.concert_schedule.starttime.data
            end = form.concert_schedule.endtime.data
            print(date)
            print(start)
            print(end)
            print("Model date " + str(model.concert_schedule.date) + " starttime " + str(model.concert_schedule.starttime) + " endtime " + str(model.concert_schedule.endtime))

            schedule = ConcertSchedule.query.filter_by(
                date = model.concert_schedule.date,
                starttime = model.concert_schedule.starttime,
                endtime = model.concert_schedule.endtime
            ).first()
            if schedule:
                schedule_id = schedule.id
            else:
                schedule_id = None

            schedule_id = model.concert_schedule.id if model.concert_schedule else None
            if start is None or end is None:
                # Solo data esistente, controlla che non ci siano schedule con la stessa data
                existing_sched = ConcertSchedule.query.filter_by(date=date).first()
                if existing_sched and existing_sched.concert and existing_sched.concert.id != model.id:
                    flash("A concert schedule with this date already exists.", "error")
                    return False
            else:
                # Data + starttime + endtime → controllo sovrapposizione
                print("Model date " + str(date) + " starttime " + str(start) + " endtime " + str(end))
                existing_sched = ConcertSchedule.query.filter(
                    ConcertSchedule.date == date,
                    ConcertSchedule.starttime <= start,
                    ConcertSchedule.endtime >= end,
                    ConcertSchedule.id != schedule_id
                ).first()
                if existing_sched:

                    print("ehilssssssssssssssssssssssssss")
                    flash(
                        f"This concert schedule conflicts with an existing one {existing_sched.date} "
                        f"({existing_sched.starttime.strftime('%H:%M')} - {existing_sched.endtime.strftime('%H:%M')}).",
                        "danger"
                    )
                    return False
        
        
            if not schedule:
                schedule = ConcertSchedule(date=date, starttime=start, endtime=end)

                

            # Assegna i record al modello
            model.ticket = ticket
            model.concert_schedule = schedule

            form.populate_obj(model)
            

            # Validazione model (ancora no add)
            if not self.validate_model(model):
                self.session.rollback()
                flash(f"Fail to validate concert", "error")
                return False

            # Solo ora salvo
            self.session.add(model)
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            flash(f"Fail to update concert: excpetion {str(e)} with traceback {str(e.__traceback__)}", "error")
            return False

    def validate_model(self, model):
        model_ticket = model.ticket
        model_ticket_link = model_ticket.ticket_link if model_ticket else None
        model_schedule = model.concert_schedule
        model_schedule_date = model_schedule.date if model_schedule else None
        model_schedule_starttime = model_schedule.starttime if model_schedule else None
        model_schedule_endtime = model_schedule.endtime if model_schedule else None
        model_place = model.place

        print("Model date " + str(model_schedule_date) + " starttime " + str(model_schedule_starttime) + " endtime " + str(model_schedule_endtime))
         
        if not model_ticket:
            flash("Select a ticket", "error")
            return False

        if not model_schedule:
            flash("Select a concert schedule", "error")
            return False


        schedule = ConcertSchedule.query.filter_by(
                date = model_schedule_date,
                starttime = model_schedule_starttime,
                endtime = model_schedule_endtime
            ).first()
        
        if schedule:
            schedule_id = schedule.id
        else:
            schedule_id = None        
        
    
        if model_ticket_link:
            existing_ticket = Ticket.query.filter(
                Ticket.ticket_link == model_ticket_link,
                Ticket.ticket_link.isnot(None),
                Ticket.ticket_link != ''
            ).first()

            if existing_ticket and existing_ticket.concert and existing_ticket.concert.id != model.id:
                flash("This ticket is already used.", "error")
                return False
        

        existing_sched = ConcertSchedule.query.filter_by(
                date=model_schedule_date,
                starttime=model_schedule_starttime,
                endtime=model_schedule_endtime
            ).first()
        
        if existing_sched and existing_sched.concert and existing_sched.concert.id != model.id:
            flash("This concert schedule is already used for another concert.", "error")
            return False

        # Controllo schedule
        if not model_schedule_date:
            flash("You must select a date for the concert schedule.", "error")
            return False

        if model_schedule_starttime is None or model_schedule_endtime is None:
            # Solo data esistente, controlla che non ci siano schedule con la stessa data
            existing_sched = ConcertSchedule.query.filter_by(date=model_schedule_date).first()
            if existing_sched and existing_sched.concert and existing_sched.concert.id != model.id:
                flash("A concert schedule with this date already exists.", "error")
                return False
        else:
            # Data + starttime + endtime → controllo sovrapposizione
            print("Model date " + str(model_schedule_date) + " starttime " + str(model_schedule_starttime) + " endtime " + str(model_schedule_endtime))
            existing_sched = ConcertSchedule.query.filter(
                ConcertSchedule.date == model_schedule_date,
                ConcertSchedule.starttime <= model_schedule_starttime,
                ConcertSchedule.endtime >= model_schedule_endtime,
                ConcertSchedule.id != (model_schedule.id if model_schedule else None)
            ).first()
            if existing_sched:
                print("ehilsssss")
                flash(
                    f"This concert schedule conflicts with an existing one {existing_sched.date} "
                    f"({existing_sched.starttime.strftime('%H:%M')} - {existing_sched.endtime.strftime('%H:%M')}).",
                    "danger"
                )
                return False

        
        existing = (
            Concert.query
            .filter(Concert.place_id == model_place.id, Concert.id != model.id)
            .filter(Concert.ticket_id == model_ticket.id,
                    Concert.concert_schedule_id == model_schedule.id)
                    .first()
                    )
        if existing:
            flash("A concert with the same place, ticket, and schedule already exists.", "error")
            return False
           
            
        return True
    
    def is_visible(self):
        return Profile.query.first() is not None


# --- Tour Admin ---
class TourAdmin(AdminView):
    column_list = ['id', 'name', 'description', 'startdate', 'enddate', 'concerts']
    form_columns = ['name', 'description', 'startdate', 'enddate', 'concerts']

    form_extra_fields = {
        'startdate': DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()]),
        'enddate': DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()]),
        'concerts': SelectMultipleField(
            'Concerts',
            coerce=int,
            widget=Select2Widget(multiple=True)
        )
    }

    form_excluded_columns = ['tour_schedule', 'concerts']

    column_formatters = {
        'startdate': lambda v, c, m, p: m.tour_schedule.startdate if m.tour_schedule else None,
        'enddate': lambda v, c, m, p: m.tour_schedule.enddate if m.tour_schedule else None,
        'concerts': lambda v, c, m, p: Markup("<br>".join(
            f"{c.place.venue if c.place else 'No place'} — "
            f"{c.concert_schedule.date if c.concert_schedule else 'No date'}"
            for c in m.concerts
        ))
    }

    def __init__(self, model, session, admin_authenticator: AdminAuthenticator, app, **kwargs):
        self.app = app
        super().__init__(model, session, admin_authenticator, **kwargs)

    # --- Prefill choices ---
    def _set_concert_choices(self, form, obj=None):
        free_concerts = Concert.query.filter(Concert.tour_id == None).all()
        current_concerts = obj.concerts if obj else []
        concerts = {c.id: c for c in free_concerts + current_concerts}.values()
        form.concerts.choices = [
            (c.id, f"[{c.id}] {c.place.venue if c.place else 'No place'} - "
                f"{c.concert_schedule.date if c.concert_schedule else 'No date'}")
            for c in concerts
        ]
        if obj:
            form.concerts.data = [c.id for c in current_concerts]  # deve essere array di ID

    def create_form(self, obj=None):
        form = super().create_form(obj)
        self._set_concert_choices(form, obj)
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        self._set_concert_choices(form, obj)

        if obj and obj.tour_schedule:
            print(form.startdate.data)
            print(form.enddate.data)
            if not request.form:
                form.startdate.data = obj.tour_schedule.startdate
                form.enddate.data = obj.tour_schedule.enddate
                print(form.startdate.data)
                print(form.enddate.data)
            
        if obj:
            form.concerts.data = [c.id for c in obj.concerts]
        
        return form

    # --- Create model manuale ---
    def create_model(self, form):
        model = self.model()
        try:
            
            # Validate form data
            if not self.validate_model(model, form):
                return False

            # Get form data
            startdate = form.startdate.data
            enddate = form.enddate.data

            # Create model
            model.name = form.name.data
            model.description = form.description.data
            
            ts = TourSchedule(startdate=startdate, enddate=enddate)
            model.tour_schedule = ts
            self.session.add(ts)

            # Leggi correttamente tutti i concerti selezionati
            selected_ids = request.form.getlist('concerts')
            selected_ids = [int(i) for i in selected_ids]
            selected_concerts = Concert.query.filter(Concert.id.in_(selected_ids)).all()
            model.concerts = selected_concerts

            self.session.add(model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            flash(f"Fail to create Tour {model.name} - ({startdate}-{enddate}) with concerts ({str(selected_ids)})", "error")
            return False


    def update_model(self, form, model):
        try:
            
            if not self.validate_model(model, form):
                return False
            

            print("Form raw:", request.form)
            print("Form parsed startdate:", form.startdate.data)
            print("Form parsed enddate:", form.enddate.data)

            startdate = form.startdate.data
            enddate = form.enddate.data

            model.name = form.name.data
            model.description = form.description.data

            if model.tour_schedule:
                print('Update - Model Values')
                model.tour_schedule.startdate = startdate
                model.tour_schedule.enddate = enddate
                print(model.tour_schedule.startdate)
                print(model.tour_schedule.enddate)
            else:
                print('Create')
                ts = TourSchedule(startdate=startdate, enddate=enddate)
                model.tour_schedule = ts
                print(model.tour_schedule.startdate)
                print(model.tour_schedule.enddate)
                self.session.add(ts)
            
            selected_ids = request.form.getlist('concerts')
            selected_ids = [int(i) for i in selected_ids]
            selected_concerts = Concert.query.filter(Concert.id.in_(selected_ids)).all()
            model.concerts = selected_concerts

            self.session.add(model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            flash(f"Fail to edit Tour {model.name} - ({startdate}-{enddate}) with concerts ({str(selected_ids)})", "error")
            return False
        
    def validate_model(self, model, form):

        startdate = form.startdate.data
        enddate = form.enddate.data
        
        selected_ids = form.concerts.data or []
        selected_concerts = Concert.query.filter(Concert.id.in_(selected_ids)).all()

        if not startdate:
            flash("Select a startdate", "error")
            return False
        if not enddate:
            flash("Select an enddate", "error")
            return False
        if startdate > enddate:
            flash(f"Start date {startdate} cannot be after end date {enddate}", "error")
            return False
        
        for c in selected_concerts:
            if c.tour_id is not None and c.tour_id != model.id:
                flash(f"Concert ID={c.id} already associated to Tour ID={c.tour_id}", "error")
                return False
            if c.concert_schedule.date < startdate or c.concert_schedule.date > enddate:
                flash(f"Concert ID={c.id} date {c.concert_schedule.date} out of Tour ID={c.tour_id} dates ({startdate}-{enddate})", "error")
                return False
            
        return True
    
    def is_visible(self):
        return Profile.query.first() is not None
    
