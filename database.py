from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, time

db = SQLAlchemy()

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(200))

    contact = db.relationship(
        "Contact",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )
    music_channels = db.relationship(
        "MusicChannels",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )
    socials = db.relationship(
        "Socials",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    profile_id = db.Column(db.Integer, db.ForeignKey("profile.id"), unique=True)
    profile = db.relationship("Profile", back_populates="contact")

class MusicChannels(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_link = db.Column(db.String(200))
    youtube_link = db.Column(db.String(200))
    applemusic_link = db.Column(db.String(200))
    profile_id = db.Column(db.Integer, db.ForeignKey("profile.id"), unique=True)
    profile = db.relationship("Profile", back_populates="music_channels")

class Socials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facebook_link = db.Column(db.String(200))
    instagram_link = db.Column(db.String(200))
    profile_id = db.Column(db.Integer, db.ForeignKey("profile.id"), unique=True)
    profile = db.relationship("Profile", back_populates="socials")
            
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(200))
    spotify_link = db.Column(db.String(200))
    youtube_link = db.Column(db.String(200))
    applemusic_link = db.Column(db.String(200))

class Address(db.Model):
    __tablename__ = "address"

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100))
    region = db.Column(db.String(100))
    province = db.Column(db.String(100))
    cap = db.Column(db.String(10))  # String per gestire zeri iniziali
    city = db.Column(db.String(100))
    street = db.Column(db.String(100))
    nr = db.Column(db.String(10))  

    places = db.relationship("Place", back_populates="address", cascade="all, delete-orphan")  # 1–N

    def __str__(self):
        return f"{self.country}, {self.region}, {self.province}, {self.cap} {self.city}, {self.street} {self.nr}"

class Place(db.Model):
    __tablename__ = "place"

    id = db.Column(db.Integer, primary_key=True)
    address_id = db.Column(db.Integer, db.ForeignKey("address.id"))
    
    venue = db.Column(db.String(100), nullable=True)
    maps_link = db.Column(db.String(300), nullable=True)

    address = db.relationship("Address", back_populates="places")
    concerts = db.relationship("Concert", back_populates="place")  # N–1

    def __str__(self):
        return self.venue

class Ticket(db.Model):
    __tablename__ = "ticket"
    id = db.Column(db.Integer, primary_key=True)
    ticket_link = db.Column(db.String(255), nullable=True, default=None, unique=True)
    is_free = db.Column(db.Boolean, nullable=True, default=True)
    concert = db.relationship("Concert", back_populates="ticket", uselist=False)
    def __repr__(self):
        return f"<Ticket {self.ticket_link}>"

class ConcertSchedule(db.Model):
    __tablename__ = "concert_schedule"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    starttime = db.Column(db.Time, nullable=True)
    endtime = db.Column(db.Time, nullable=True)
    concert = db.relationship("Concert", back_populates="concert_schedule", uselist=False)
    def __repr__(self):
        return f"<Schedule {self.date} {self.starttime}-{self.endtime}>"

class Concert(db.Model):
    __tablename__ = "concert"
    id = db.Column(db.Integer, primary_key=True)
    
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
    place = db.relationship("Place", back_populates="concerts")
    
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), unique=True)
    ticket = db.relationship("Ticket", back_populates="concert")  # many-to-one
    
    concert_schedule_id = db.Column(db.Integer, db.ForeignKey('concert_schedule.id'))
    concert_schedule = db.relationship("ConcertSchedule", back_populates="concert")  # many-to-one
    
    tour_id = db.Column(db.Integer, db.ForeignKey("tour.id"), nullable=True)
    tour = db.relationship("Tour", back_populates="concerts")

    def __str__(self):
        return f"{self.place.venue if self.place else ''}, {self.concert_schedule.date if self.concert_schedule else ''}, "

class TourSchedule(db.Model):
    __tablename__ = "tour_schedule"

    id = db.Column(db.Integer, primary_key=True)
    startdate = db.Column(db.Date, nullable=False)
    enddate = db.Column(db.Date, nullable=False)

    tour_id = db.Column(db.Integer, db.ForeignKey("tour.id"), unique=True)
    tour = db.relationship("Tour", back_populates="tour_schedule", uselist=False)

    def __str__(self):
        return f"{self.tour.name} ({self.startdate} - {self.enddate})"

class Tour(db.Model):
    __tablename__ = "tour"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    concerts = db.relationship("Concert", back_populates="tour")  # Tour → Concerts
    tour_schedule = db.relationship("TourSchedule", back_populates="tour", uselist=False, cascade="all, delete-orphan")

    def __str__(self):
        return self.name

class BoardMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class PageDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)