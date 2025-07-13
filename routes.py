# Main application routes (user and admin views)
# routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from models import db, User, StaffProfile, LeaveRequest, Invite
from forms import ProfileForm, LeaveForm, EditContactForm
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from werkzeug.utils import secure_filename
from flask import current_app
from flask_mail import Message
import secrets
# from app import mail  # Ensure you have mail configured in your app
#  # Import mail from your app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        users = User.query.all()
        profiles = StaffProfile.query.all()
        leave_requests = LeaveRequest.query.all()
        return render_template('admin_dashboard.html', users=users, profiles=profiles, leave_requests=leave_requests)
    else:
        profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
        leave_notifications = LeaveRequest.query.filter_by(user_id=current_user.id).filter(LeaveRequest.status != 'pending').all()
        return render_template(
            'user_dashboard.html',
            profile=profile,
            leave_notifications=leave_notifications
        )

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    if profile and profile.is_submitted:
        flash('Profile already submitted.', 'info')
        return redirect(url_for('main.dashboard'))

    if form.validate_on_submit():
        new_profile = StaffProfile(
            user_id=current_user.id,
            phone=form.phone.data,
            age=form.age.data,
            ministry=form.ministry.data,
            department=form.department.data,
            role=form.role.data,
            year_of_office=form.year_of_office.data,
            address=form.address.data,
            is_submitted=True
        )
        db.session.add(new_profile)
        db.session.commit()
        flash('Profile submitted successfully.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('profile_form.html', form=form, profile=profile)

@main_bp.route('/edit_contact', methods=['GET', 'POST'])
@login_required
def edit_contact():
    form = EditContactForm()
    if form.validate_on_submit():
        if form.passport_photo.data:
            filename = secure_filename(form.passport_photo.data.filename)
            photo_path = os.path.join('static', 'uploads', 'profile_photos', filename)
            form.passport_photo.data.save(photo_path)
            current_user.profile.passport_photo = filename
            db.session.commit()
        current_user.profile.phone = form.phone.data
        db.session.commit()
        flash('Contact info updated.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_contact.html', form=form)

@main_bp.route('/leave', methods=['GET', 'POST'])
@login_required
def leave():
    form = LeaveForm()
    if form.validate_on_submit():
        leave = LeaveRequest(user_id=current_user.id, reason=form.reason.data, date_submitted=datetime.utcnow())
        db.session.add(leave)
        db.session.commit()
        flash('Leave request submitted.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('leave_requests.html', form=form)

@main_bp.route('/view_staff')
@login_required
def view_staff():
    staff = StaffProfile.query.all()
    return render_template('view_staff.html', staff=staff)

@main_bp.route('/pay_info')
@login_required
def pay_info():
    # Placeholder view for user pay info/schedule
    return render_template('pay_info.html')

@main_bp.route('/export_staff_pdf')
@login_required
def export_staff_pdf():
    staff = StaffProfile.query.all()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "Staff List")
    y -= 30
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "ID")
    p.drawString(80, y, "Name")
    p.drawString(200, y, "Phone")
    p.drawString(300, y, "Ministry")      # Added ministry header
    p.drawString(380, y, "Department")
    p.drawString(480, y, "Role")
    p.drawString(540, y, "Year")
    y -= 20
    p.setFont("Helvetica", 10)

    for s in staff:
        if y < 40:
            p.showPage()
            y = height - 40
        user_name = s.user.name if s.user else "N/A"
        phone = s.phone if s.phone else "N/A"
        ministry = s.ministry if s.ministry else "N/A"      # Added ministry value
        department = s.department if s.department else "N/A"
        role = s.role if s.role else "N/A"
        year = str(s.year_of_office) if s.year_of_office else "N/A"

        p.drawString(40, y, str(s.id))
        p.drawString(80, y, user_name)
        p.drawString(200, y, phone)
        p.drawString(300, y, ministry)      # Added ministry value
        p.drawString(380, y, department)
        p.drawString(480, y, role)
        p.drawString(540, y, year)
        y -= 20

    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="staff_list.pdf", mimetype='application/pdf')

@main_bp.route('/approve_leave/<int:leave_id>', methods=['POST'])
@login_required
def approve_leave(leave_id):
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.dashboard'))
    leave = LeaveRequest.query.get_or_404(leave_id)
    leave.status = 'approved'
    db.session.commit()
    flash('Leave request approved.', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/decline_leave/<int:leave_id>', methods=['POST'])
@login_required
def decline_leave(leave_id):
    if current_user.role != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('main.dashboard'))
    leave = LeaveRequest.query.get_or_404(leave_id)
    leave.status = 'declined'
    db.session.commit()
    flash('Leave request declined.', 'warning')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/user_notifications')
@login_required
def user_notifications():
    leave_notifications = LeaveRequest.query.filter_by(user_id=current_user.id).filter(LeaveRequest.status != 'pending').all()
    return render_template('user_notifications.html', leave_notifications=leave_notifications)

@main_bp.route('/invite_staff', methods=['GET', 'POST'])
@login_required
def invite_staff():
    from app import mail
    if current_user.role != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please provide an email address.', 'warning')
            return redirect(url_for('main.invite_staff'))
        existing = Invite.query.filter_by(email=email, used=False).first()
        if existing:
            flash('An invite has already been sent to this email.', 'warning')
            return redirect(url_for('main.invite_staff'))
        token = secrets.token_urlsafe(32)
        invite = Invite(email=email, token=token)
        db.session.add(invite)
        db.session.commit()
        invite_url = url_for('auth.register', token=token, _external=True)
        msg = Message('Staff Registration Invite', recipients=[email])
        msg.body = f"Hello,\n\nYou have been invited to register as staff. Please use the following link to register:\n{invite_url}\n\nIf you did not expect this, you can ignore this email."
        try:
            mail.send(msg)
            flash('Invitation sent!', 'success')
        except Exception as e:
            print("Mail send error:", e)  # This will show the error in your terminal
            flash('Failed to send email. Please check your mail configuration.', 'danger')
        return redirect(url_for('main.invite_staff'))
    return render_template('invite_staff.html')  

# @main_bp.route('/test_mail')
# def test_mail():
#     from flask_mail import Message
#     msg = Message("Test Email", recipients=["adedokunjesupelumi@gmail.com"])
#     msg.body = "This is a test."
#     try:
#         mail.send(msg)
#         return "Mail sent!"
#     except Exception as e:
#         import traceback
#         print("Mail send error:", e)
#         traceback.print_exc()
#         return f"Mail failed: {e}"