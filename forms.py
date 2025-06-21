from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField, DateField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, NumberRange, EqualTo, ValidationError
from models import User, NatureSpot

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(5, '5 stars - Excellent'), (4, '4 stars - Very Good'), 
                                           (3, '3 stars - Good'), (2, '2 stars - Fair'), 
                                           (1, '1 star - Poor')], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Review Comment', validators=[Length(max=1000)])
    visit_date = DateField('Visit Date', validators=[DataRequired()])
    photos = FileField('Upload Photos (minimum 2)', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Submit Review')

class SpotFilterForm(FlaskForm):
    district = SelectField('District', choices=[('', 'All Districts')], default='')
    spot_type = SelectField('Type', choices=[('', 'All Types'), ('hill', 'Hill'), ('lake', 'Lake'), 
                                           ('forest', 'Forest'), ('waterfall', 'Waterfall'), 
                                           ('cave', 'Cave'), ('valley', 'Valley')], default='')
    difficulty = SelectField('Difficulty', choices=[('', 'All Levels'), ('easy', 'Easy'), 
                                                   ('moderate', 'Moderate'), ('hard', 'Hard')], default='')
    max_distance = IntegerField('Max Distance (km)', validators=[NumberRange(min=1, max=500)])
    submit = SubmitField('Filter')

class AddSpotForm(FlaskForm):
    name = StringField('Spot Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    district = SelectField('District', choices=[
        ('Kathmandu', 'Kathmandu'), ('Lalitpur', 'Lalitpur'), ('Bhaktapur', 'Bhaktapur'),
        ('Pokhara', 'Pokhara'), ('Chitwan', 'Chitwan'), ('Banke', 'Banke'),
        ('Dang', 'Dang'), ('Kailali', 'Kailali'), ('Kanchanpur', 'Kanchanpur'),
        ('Dolakha', 'Dolakha'), ('Ramechhap', 'Ramechhap'), ('Sindhuli', 'Sindhuli'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired(), NumberRange(min=26, max=31)])
    longitude = FloatField('Longitude', validators=[DataRequired(), NumberRange(min=80, max=89)])
    altitude = IntegerField('Altitude (meters)', validators=[NumberRange(min=0, max=9000)])
    spot_type = SelectField('Type', choices=[('hill', 'Hill'), ('lake', 'Lake'), ('forest', 'Forest'), 
                                           ('waterfall', 'Waterfall'), ('cave', 'Cave'), ('valley', 'Valley')], 
                          validators=[DataRequired()])
    difficulty_level = SelectField('Difficulty Level', choices=[('easy', 'Easy'), ('moderate', 'Moderate'), ('hard', 'Hard')])
    best_season = StringField('Best Season to Visit', validators=[Length(max=50)])
    entry_fee = FloatField('Entry Fee (NPR)', validators=[NumberRange(min=0)])
    submit = SubmitField('Add Spot')

class CommunityTipForm(FlaskForm):
    tip_type = SelectField('Tip Type', choices=[('packing', 'Packing Tips'), ('food', 'Food & Restaurants'), 
                                              ('transport', 'Transportation'), ('season', 'Best Season'),
                                              ('safety', 'Safety Tips'), ('other', 'Other')], 
                         validators=[DataRequired()])
    content = TextAreaField('Your Tip', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Share Tip')

class RoadUpdateForm(FlaskForm):
    status = SelectField('Road Status', choices=[('smooth', 'Smooth'), ('damaged', 'Damaged'), 
                                               ('construction', 'Under Construction'), ('landslide', 'Landslide Prone')], 
                       validators=[DataRequired()])
    description = TextAreaField('Additional Details', validators=[Length(max=500)])
    submit = SubmitField('Update Road Status')

class ProfileEditForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    profile_image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update Profile')
