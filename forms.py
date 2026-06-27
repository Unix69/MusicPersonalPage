from flask import flash
from wtforms import FileField, Form, StringField, TextAreaField, BooleanField, DateField, TimeField, ValidationError
from wtforms.validators import DataRequired, Optional, Length, Regexp, Email
from flask_wtf.file import FileAllowed
from validators import FormValidators


    
class ProfileForm(Form):
    name = StringField(
        'Name', 
        validators=[
            DataRequired(),
            Length(min=8, max=32),
            Regexp(r'^[a-zA-Z0-9\s\-]+$', message="Name can contain only letters, numbers, spaces, hyphens."),
            FormValidators.no_html,
            FormValidators.no_sql
        ]
    )

    bio = TextAreaField(
        'Bio',
        validators=[
            Optional(),
            Length(min=0, max=1024),
            FormValidators.no_html,
            FormValidators.no_sql
        ]
    )

    profile_image = FileField(
        'Profile Image',
        validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')]
    )


    email = StringField(
        'Email',
        validators=[
            Optional(),
            Email(message="Invalid email address."),
            FormValidators.no_html,
            FormValidators.no_sql
        ]
    )

    phone = StringField(
        'Phone',
        validators=[
            Optional(),
            FormValidators.no_html,
            FormValidators.no_sql,
            Length(min=7, max=15),
            Regexp(r'^\+?\d{7,15}$', message="Invalid phone number. Only digits and optional leading +.")
        ]
    )


    spotify_link = StringField(
        'Spotify Link',
        validators=[Optional(), FormValidators.no_html, FormValidators.no_sql, FormValidators.url_validator_factory(allowed_domains="spotify.com", field_name="Spotify Link")]
    )
    youtube_link = StringField(
        'YouTube Link',
        validators=[Optional(), FormValidators.no_html, FormValidators.no_sql, FormValidators.url_validator_factory(allowed_domains=["youtube.com", "youtu.be"], field_name="YouTube Link")]
    )
    applemusic_link = StringField(
        'Apple Music Link',
        validators=[Optional(), FormValidators.no_html, FormValidators.no_sql, FormValidators.url_validator_factory(allowed_domains="music.apple.com", field_name="Apple Music Link")]
    )

    # Socials
    facebook_link = StringField(
        'Facebook Link',
        validators=[Optional(), FormValidators.no_html, FormValidators.no_sql, FormValidators.url_validator_factory(allowed_domains="facebook.com", field_name="Facebook Link")]
    )
    instagram_link = StringField(
        'Instagram Link',
        validators=[Optional(), FormValidators.no_html, FormValidators.no_sql, FormValidators.url_validator_factory(allowed_domains="instagram.com", field_name="Instagram Link")]
    )


class TicketForm(Form):
    is_free = BooleanField('Is Free', default=True, validators=[Optional()], render_kw={"class": "ticket-isfree form-check-input"})
    ticket_link = StringField('Ticket Link', validators=[Optional(), FormValidators.no_html, FormValidators.no_sql, FormValidators.url_validator_factory(field_name="Ticket Link")],
                              render_kw={"class": "ticket-link form-control"}, filters=[lambda x: x or None])


class ConcertScheduleForm(Form):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()],
                     render_kw={"class": "schedule-date form-control"})
    starttime = TimeField('Start Time', format='%H:%M', validators=[Optional()],
                          render_kw={"class": "schedule-starttime form-control"})
    endtime = TimeField('End Time', format='%H:%M', validators=[Optional()],
                        render_kw={"class": "schedule-endtime form-control"})
    
    def validate_endtime(self, field):
        if self.starttime.data and field.data:
            if self.starttime.data > field.data:
                flash("Start time cannot be after end time", "error")
                raise ValidationError("Start time cannot be after end time")