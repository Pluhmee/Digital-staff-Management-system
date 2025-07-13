# Flask-WTF forms for login, registration, and profile update
# forms.py
# from forms import ProfileForm
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    age = IntegerField('Age', validators=[DataRequired()])
    ministry = StringField('Ministry', validators=[DataRequired()])
    department = StringField('Department', validators=[DataRequired()])
    role = StringField('Role', validators=[DataRequired()])
    year_of_office = StringField('Year of Office', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])
    passport_photo = FileField('Passport Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Submit Profile')

class LeaveForm(FlaskForm):
    reason = TextAreaField('Reason for Leave', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Submit Leave Request')

class EditContactForm(FlaskForm):
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    passport_photo = FileField('Passport Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Update Contact')

