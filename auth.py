# Authentication routes: login, register, logout
# auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Invite
from forms import LoginForm, RegisterForm
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message

auth_bp = Blueprint('auth', __name__)

def generate_reset_token(email, secret_key, expires_sec=3600):
    s = URLSafeTimedSerializer(secret_key)
    return s.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, secret_key, expires_sec=3600):
    s = URLSafeTimedSerializer(secret_key)
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
    except Exception:
        return None
    return email

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # token = request.args.get('token')
    # if not token:
    #     flash('Registration requires a valid invite link.', 'danger')
    #     return redirect(url_for('auth.login'))
    # invite = Invite.query.filter_by(token=token, used=False).first()
    # if not invite:
    #     flash('Invalid or expired invite link.', 'danger')
    #     return redirect(url_for('auth.login'))
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            # return redirect(url_for('auth.register', token=token))
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password,
            role='user'
        )
        db.session.add(new_user)
        # invite.used = True  # Mark invite as used
        db.session.commit()
        flash('Registration successful. You can now login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        from app import mail  # <-- Import here to avoid circular import
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email, current_app.config['SECRET_KEY'])
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            msg = Message('Password Reset Request',
                          recipients=[user.email])
            msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email.
'''
            mail.send(msg)
            flash('Password reset instructions have been sent to your email.', 'info')
        else:
            flash('No account found with that email.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    return render_template('forgot_password.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token, current_app.config['SECRET_KEY'])
    if not email:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    if request.method == 'POST':
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('Your password has been updated. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('auth.forgot_password'))
    return render_template('reset_password.html')