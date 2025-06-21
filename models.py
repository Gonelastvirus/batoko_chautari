from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    profile_image = db.Column(db.String(200), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)
    badge_title = db.Column(db.String(50), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    visits = db.relationship('Visit', backref='user', lazy=True, cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('Photo', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_badge_title(self):
        if self.points >= 1000:
            return "Trailblazer"
        elif self.points >= 500:
            return "Hidden Gem Hunter"
        elif self.points >= 200:
            return "Explorer"
        elif self.points >= 50:
            return "Wanderer"
        else:
            return "Newcomer"
    
    def update_badge(self):
        self.badge_title = self.get_badge_title()

class NatureSpot(db.Model):
    __tablename__ = 'nature_spots'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    district = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    altitude = db.Column(db.Integer, nullable=True)  # in meters
    spot_type = db.Column(db.String(50), nullable=False)  # hill, lake, forest, waterfall, cave, etc.
    difficulty_level = db.Column(db.String(20), nullable=True)  # easy, moderate, hard
    best_season = db.Column(db.String(50), nullable=True)
    entry_fee = db.Column(db.Float, nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    road_status = db.Column(db.String(50), default='unknown')  # smooth, damaged, construction, landslide
    last_road_update = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='nature_spot', lazy=True, cascade='all, delete-orphan')
    visits = db.relationship('Visit', backref='nature_spot', lazy=True, cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='nature_spot', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('Photo', backref='nature_spot', lazy=True, cascade='all, delete-orphan')
    tips = db.relationship('CommunityTip', backref='nature_spot', lazy=True, cascade='all, delete-orphan')
    
    def get_average_rating(self):
        if self.reviews:
            return sum(review.rating for review in self.reviews) / len(self.reviews)
        return 0
    
    def get_approved_photos(self):
        return [photo for photo in self.photos if photo.is_approved]

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nature_spot_id = db.Column(db.Integer, db.ForeignKey('nature_spots.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    visit_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    photos = db.relationship('Photo', backref='review', lazy=True, cascade='all, delete-orphan')

class Photo(db.Model):
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nature_spot_id = db.Column(db.Integer, db.ForeignKey('nature_spots.id'), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=True)
    filename = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(500), nullable=True)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_cover_photo = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)

class Visit(db.Model):
    __tablename__ = 'visits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nature_spot_id = db.Column(db.Integer, db.ForeignKey('nature_spots.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    has_reviewed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nature_spot_id = db.Column(db.Integer, db.ForeignKey('nature_spots.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'nature_spot_id'),)

class CommunityTip(db.Model):
    __tablename__ = 'community_tips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nature_spot_id = db.Column(db.Integer, db.ForeignKey('nature_spots.id'), nullable=False)
    tip_type = db.Column(db.String(50), nullable=False)  # packing, food, transport, season
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='tips')

class RoadUpdate(db.Model):
    __tablename__ = 'road_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nature_spot_id = db.Column(db.Integer, db.ForeignKey('nature_spots.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # smooth, damaged, construction, landslide
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='road_updates')
    nature_spot = db.relationship('NatureSpot', backref='road_updates')
