

from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from flask_wtf.file import FileAllowed, FileField

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import shutil
import os
import random
import string
from datetime import datetime, timedelta, time
import uuid
from sqlalchemy.sql import func
from pytz import timezone, utc
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.fields.choices import RadioField
from wtforms.fields.datetime import DateTimeLocalField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, InputRequired

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'Alohomora'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt', 'png', 'jpg'}
#   ____________________Models____________________
class User(UserMixin, db.Model):


    table_name = 'users'
    id=db.Column(db.Integer, primary_key=True)
    email = db.Column(String(100), unique=True)
    password = db.Column(String(100))
    name= db.Column(String(1000))
    lastname = db.Column(String(1000))
    phonenumber= db.Column(String(1000),nullable=True)
    gender =db.Column(String(1000))
    profile_image = db.Column(String(1000), nullable=True)
    classes = db.relationship('Class', backref='instructor', lazy=True)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())




class Class(db.Model):
        table_name = 'class'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        subject = db.Column(db.String(100), nullable=False)
        day = db.Column(db.String(10), nullable=False)
        start_time = db.Column(db.Time, nullable=False)
        duration = db.Column(db.Integer, nullable=False)
        key = db.Column(db.String(10), unique=True, nullable=False)
        instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        materials = db.relationship('Material', backref='class_info', cascade='all, delete-orphan')
        homeworks = db.relationship('Homework', backref='class_info', cascade='all, delete-orphan')
        announcements = db.relationship('Announcement', backref='class_info', cascade='all, delete-orphan')
        created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

        updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())



class Material(db.Model):
    table_name = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())



class Homework(db.Model):
    table_name = 'homework'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)


    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())




class Announcement(db.Model):
    __tablename__ = 'Announcement'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
# ______________________ form classes ______________________
class LoginForm(FlaskForm):
     email=StringField('Email', validators=[DataRequired(), Email()])
     password=PasswordField('Password',validators=[DataRequired()])
     submit=SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    phonenumber = StringField('Phone Number', validators=[DataRequired(), Length(min=9, max=9)])
    gender = RadioField('Gender', choices=[
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Other', 'Other')
    ], default='Female', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])
    role=role = SelectField('Choose Your Role', choices=[
        ('Instructor', 'Instructor')], validators=[DataRequired()] )
    submit = SubmitField('Register')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phonenumber = StringField('Phone Number', validators=[Optional(), Length(min=9, max=9)])
    profile_picture = FileField('Profile Picture', validators=[Optional(), FileAllowed({'png', 'jpg'})])
    submit = SubmitField('Update Profile')

class RegisterClassForm(FlaskForm):
        name = StringField('Class Name', validators=[DataRequired(), Length(max=100)])
        subject = StringField('Subject', validators=[DataRequired(), Length(max=100)])
        day = SelectField('Day of the Week', choices=[
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday')
        ], validators=[DataRequired()])
        start_hour = IntegerField('Start Hour', validators=[
            InputRequired(), NumberRange(min=8, max=20, message="Hour must be between 8 and 20")
        ])
        start_minute = IntegerField('Start Minute', validators=[
            InputRequired(), NumberRange(min=0, max=59, message="Minute must be between 0 and 59")
        ])

        duration = IntegerField('Duration (minutes)', validators=[
            InputRequired(), NumberRange(min=1, message="Duration must be at least 1 minute")
        ])
        submit = SubmitField('Register Class')
class AddMaterialForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[Optional()])
    file = FileField('Upload File', validators=[ Optional(),  FileAllowed(ALLOWED_EXTENSIONS, 'Documents only!')
    ])
    submit = SubmitField('✅ Done')

class AddAnnouncementForm(FlaskForm):
    name = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Message', validators=[Optional()])
    submit = SubmitField('✅ Post')

class AddHomeworkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[Optional()])
    file = FileField('Upload File', validators=[Optional(), FileAllowed(['pdf', 'docx', 'pptx'])])
    deadline = DateTimeLocalField('Deadline', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    submit = SubmitField('✅ Done')
#   ____________________ AUTH____________________
@app.route('/')
def home():
    if current_user.is_authenticated:
        logout_user()
    return render_template("auth/home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        result=db.session.execute(db.select(User).where(User.email==email))
        user = result.scalar()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('instructor'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

    return render_template("auth/login.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        email=form.email.data
        existing_user=db.session.execute(db.select(User).where(User.email == email)).scalar()
        if existing_user:
            flash("An account with this email already exists.","danger")
            return redirect(url_for("register"))
        #
        hash_and_salted_password = generate_password_hash( request.form.get('password'), method='pbkdf2:sha256',
            salt_length=5
        )
        new_user = User(
            email=email,
            name=form.name.data,
            lastname=form.lastname.data,
            phonenumber=form.phonenumber.data,
            gender=form.gender.data,
            password=hash_and_salted_password,
            profile_image="profile_placeholder.png"


        )
        db.session.add(new_user)
        db.session.commit()
        instructor_dir = os.path.join(app.root_path, 'static/uploads/instructors', str(new_user.id))
        os.makedirs(os.path.join(instructor_dir, 'profile_pics'), exist_ok=True)
        os.makedirs(os.path.join(instructor_dir, 'classes'), exist_ok=True)
        flash("Registration successful! You can now log in.","success")
        return redirect(url_for("login"))
    return render_template("auth/register.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

#   ____________________ Instructor____________________

@app.route('/instructor')
@login_required
def instructor():
    user_classes = Class.query.filter_by(instructor_id=current_user.id).all()
    return render_template("user/instructor_dashboard.html", name=current_user.name, user=current_user, classes=user_classes  )

@app.route('/about', methods=['GET', 'POST'])
@login_required
def about_instructor():
    form = EditProfileForm(obj=current_user)  # pre-fill with current values
    user = current_user

    if form.validate_on_submit():
        change = False

        if form.name.data != user.name:
            user.name = form.name.data
            change = True

        if form.email.data != user.email:
            user.email = form.email.data
            change = True

        if form.phonenumber.data != user.phonenumber:
            user.phonenumber = form.phonenumber.data
            change = True

        if form.profile_picture.data:
            if user.profile_image and user.profile_image != "profile_placeholder.png":
                old_path = os.path.join(app.root_path, 'static/uploads/instructors', str(current_user.id), 'profile_pics', user.profile_image)

                delete_file_if_exists(old_path)

            ext = form.profile_picture.data.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            profile_pic_dir = os.path.join(app.root_path, 'static/uploads/instructors', str(current_user.id),
                                           'profile_pics')


            filepath = os.path.join(profile_pic_dir, filename)

            form.profile_picture.data.save(filepath)
            user.profile_image = filename


            change = True

        if change:
            user.updated_at = func.now()
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        else:
            flash("No changes were made.", 'info')

        return redirect(url_for('about_instructor'))

    return render_template('user/instructor_about.html', form=form, user=current_user, to_tbilisi=to_tbilisi)
@app.route('/curriculum')
@login_required
def curriculum():
    # old one

    today = datetime.today()

    start_of_week = datetime.combine((today - timedelta(days=today.weekday())).date(), datetime.min.time())

    end_of_week = datetime.combine((start_of_week + timedelta(days=6)).date(), datetime.max.time())


    classes = Class.query.filter_by(instructor_id=current_user.id).all()



    schedule = {i: {'classes': []} for i in range(7)}
    for c in classes:
        weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index(c.day)
        c.end_time = (datetime.combine(datetime.today(), c.start_time) + timedelta(minutes=c.duration)).time()
        schedule[weekday]['classes'].append(c)



    return render_template('user/instructor_curriculum.html', user=current_user,schedule=schedule)
@app.route('/delete_instructor')
@login_required
def delete_instructor():
    instructor_id = current_user.id


    classes = Class.query.filter_by(instructor_id=instructor_id).all()


    for cls in classes:
        delete_class(cls)
    instructor_folder = os.path.join(app.root_path, 'static/uploads/instructors', str(instructor_id))
    if os.path.exists(instructor_folder):

        shutil.rmtree(instructor_folder)

    db.session.delete(current_user)
    db.session.commit()

    logout_user()
    flash("Your account and all data were deleted.", "success")
    return redirect(url_for('home'))



# _________________Class_____________________________________
@app.route('/register_class', methods=['GET', 'POST'])
@login_required
def register_class():
    form = RegisterClassForm()

    if form.validate_on_submit():
        class_key = generate_unique_class_key()

        day = form.day.data
        duration = form.duration.data
        start_time = datetime.strptime(f"{form.start_hour.data}:{form.start_minute.data:02d}", "%H:%M").time()
        end_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=duration)).time()

        if start_time < time(8, 0) or end_time > time(20, 0):
            flash("Class must start at 08:00 or later and end by 20:00.", "danger")
            return redirect(url_for('register_class'))

        existing_classes = Class.query.filter_by(instructor_id=current_user.id, day=day).all()
        for c in existing_classes:
            class_start = c.start_time
            class_end = (datetime.combine(datetime.today(), class_start) + timedelta(minutes=c.duration)).time()
            if not (end_time <= class_start or start_time >= class_end):
                flash("This class time overlaps with another class you're teaching on the same day.", "danger")
                return redirect(url_for('register_class'))

        base_name = form.name.data
        name = base_name
        counter = 2
        while Class.query.filter_by(instructor_id=current_user.id, name=name).first():
            name = f"{base_name} ({counter})"
            counter += 1
        if name != base_name:
            flash(f'You already have a class named "{base_name}". This one was saved as "{name}".', "info")

        new_class = Class(
            name=name,
            subject=form.subject.data,
            day=day,
            start_time=start_time,
            duration=duration,
            instructor_id=current_user.id,
            key=class_key
        )

        db.session.add(new_class)
        db.session.commit()

        class_folder = os.path.join(
            app.root_path, 'static/uploads/instructors',
            str(current_user.id), 'classes', str(new_class.id)
        )
        os.makedirs(os.path.join(class_folder, 'materials'), exist_ok=True)
        os.makedirs(os.path.join(class_folder, 'homeworks'), exist_ok=True)
        flash("Class registered successfully!", "success")
        return redirect(url_for('class_dashboard', class_id=new_class.id))

    return render_template('class/registerClass.html', form=form)

@app.route('/edit_class/<int:class_id>', methods=['GET', 'POST'])
@login_required
def edit_class(class_id):
    class_info = Class.query.get_or_404(class_id)

    if class_info.instructor_id != current_user.id:
        flash("You can't edit someone else's class.", "danger")
        return redirect(url_for('class_dashboard', class_id=class_id))

    form = RegisterClassForm(obj=class_info)

    form.submit.label.text = "Save"
    if request.method == 'GET' and class_info.start_time:
        form.start_hour.data = class_info.start_time.hour
        form.start_minute.data = class_info.start_time.minute

    if form.validate_on_submit():
        new_name = form.name.data
        new_subject = form.subject.data
        new_day = form.day.data
        new_duration = form.duration.data
        new_start_time = datetime.strptime(f"{form.start_hour.data}:{form.start_minute.data:02d}", "%H:%M").time()
        new_end_time = (datetime.combine(datetime.today(), new_start_time) + timedelta(minutes=new_duration)).time()

        existing_classes = Class.query.filter(
            Class.instructor_id == current_user.id,
            Class.day == new_day,
            Class.id != class_id
        ).all()


        for c in existing_classes:
            class_start = c.start_time
            class_end = (datetime.combine(datetime.today(), class_start) + timedelta(minutes=c.duration)).time()
            if not (new_end_time <= class_start or new_start_time >= class_end):
                flash("This class time overlaps with another class you're teaching on the same day.", "danger")
                return redirect(url_for('edit_class'))

        base_name = form.name.data
        new_name = base_name
        counter = 2
        while any(c.name==new_name for c in existing_classes):
            new_name = f"{base_name} ({counter})"
            counter += 1
        if new_name != base_name:
            flash(f'You already have a class named "{base_name}". This one was saved as "{new_name}".', "info")

        if (
            class_info.name == new_name and
            class_info.subject == new_subject and
            class_info.day == new_day and
            class_info.start_time == new_start_time and
            class_info.duration == new_duration
         ):
            flash("No changes made.", "info")
            return redirect(url_for('class_dashboard', class_id=class_id))

        class_info.name = new_name
        class_info.subject = new_subject
        class_info.day = new_day
        class_info.start_time = new_start_time
        class_info.duration = new_duration
        class_info.updated_ad=func.now()
        db.session.commit()
        flash("Class updated successfully.", "success")
        return redirect(url_for('class_dashboard', class_id=class_id))

    return render_template('class/class_editabout.html', form=form, class_info=class_info, to_tbilisi=to_tbilisi)

@app.route('/class_dashboard/<int:class_id>')
@login_required
def class_dashboard(class_id):
    class_info = Class.query.get_or_404(class_id)

    return render_template('class/class_about.html', class_info=class_info, to_tbilisi=to_tbilisi)
@app.route('/delete_class/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    class_to_delete = Class.query.get_or_404(class_id)

    if class_to_delete.instructor_id != current_user.id:
        flash("You are not authorized to delete this class.", "danger")
        return redirect(url_for('instructor'))

    delete_class(class_to_delete)
    db.session.commit()

    flash('Class and all related data deleted successfully!', 'success')
    return redirect(url_for('instructor'))

#________________Material_____________________
@app.route('/materials/<int:class_id>')
@login_required
def materials(class_id):
    class_info = Class.query.get_or_404(class_id)
    materials=Material.query.filter_by(class_id=class_id).all()

    return render_template('class/material/class_materials.html', class_info=class_info, materials=materials)

@app.route('/add_material/<int:class_id>', methods=['GET', 'POST'])
@login_required
def addmaterials(class_id):
    class_info = Class.query.get_or_404(class_id)
    form = AddMaterialForm()

    if form.validate_on_submit():
        name = form.name.data
        text = form.text.data
        file = form.file.data
        filename=None
        existing = Material.query.filter_by(class_id=class_info.id, name=name).first()
        if existing:
            flash(f'A material named "{name}" already exists in this class.', "danger")
            return redirect(url_for('materials', class_id=class_info.id))

        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            materials_path = os.path.join(
                app.root_path, 'static/uploads/instructors',
                str(current_user.id), 'classes', str(class_info.id), 'materials'
            )
            os.makedirs(materials_path, exist_ok=True)

            file_path = os.path.join(materials_path, filename)
            file.save(file_path)
        elif file and not allowed_file(file.filename):

            flash('Invalid file format.', 'danger')
            return redirect(request.url)

        material = Material(
                name=name,
                text=text,
                filename=filename,
                class_id=class_info.id
            )
        db.session.add(material)
        db.session.commit()

        flash('Material uploaded successfully!', 'success')
        return redirect(url_for('materials', class_id=class_info.id))




    return render_template('class/material/class_addmaterial.html', class_info=class_info, form=form)
@app.route('/material/<int:material_id>')
@login_required
def view_material(material_id):
    material = Material.query.get_or_404(material_id)
    class_info=material.class_info

    return render_template('class/material/class_viewmaterial.html', material=material, class_info= class_info, to_tbilisi=to_tbilisi)
@app.route('/edit_material/<int:material_id>', methods=['GET', 'POST'])
@login_required
def edit_material(material_id):
    material = Material.query.get_or_404(material_id)

    if material.class_info.instructor_id != current_user.id:
        flash("You can’t edit material from another instructor’s class.", "danger")
        return redirect(url_for('materials', class_id=material.class_id))

    form = AddMaterialForm(obj=material)

    if form.validate_on_submit():
        change = False

        if form.name.data != material.name:
            new_name = form.name.data.strip()
            existing = Material.query.filter(
                Material.class_id == material.class_id,
                Material.name == new_name,
                Material.id != material.id
            ).first()

            if existing:
                flash(f'A material named "{new_name}" already exists in this class.', "danger")
                return redirect(url_for('view_material', material_id=material_id))
            material.name = form.name.data
            change = True

        if form.text.data != material.text:
            material.text = form.text.data
            change = True

        file = form.file.data
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"

            materials_dir = os.path.join(
                app.root_path, 'static/uploads/instructors',
                str(current_user.id), 'classes',
                str(material.class_id), 'materials'
            )
            os.makedirs(materials_dir, exist_ok=True)

            file_path = os.path.join(materials_dir, filename)


            if material.filename:
                old_file = os.path.join(materials_dir, material.filename)
                delete_file_if_exists(old_file)

            file.save(file_path)
            material.filename = filename
            change = True

        if change:
            material.updated_at = func.now()
            db.session.commit()
            flash("Material updated successfully.", "success")
        else:
            flash("No changes were made.", "info")

        return redirect(url_for('view_material', material_id=material.id))

    return render_template('class/material/class_editmaterial.html', form=form, material=material, class_info=material.class_info)
@app.route('/delete_material/<int:material_id>', methods=['POST'])
@login_required
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    class_info = material.class_info

    if class_info.instructor_id != current_user.id:
        flash("You are not authorized to delete this material.", "danger")
        return redirect(url_for('materials', class_id=class_info.id))

    delete_material(material)
    db.session.commit()

    flash("Material deleted successfully!", "success")
    return redirect(url_for('materials', class_id=class_info.id))

@app.route('/download/<int:class_id>/materials/<filename>')
@login_required
def download_material(class_id, filename):
    class_info = Class.query.get_or_404(class_id)

    if class_info.instructor_id != current_user.id:
        flash("You are not authorized to download this file.", "danger")
        return redirect(url_for('materials', class_id=class_id))

    folder = os.path.join(
        app.root_path, 'static/uploads/instructors',
        str(current_user.id), 'classes', str(class_id), 'materials'
    )

    return send_from_directory(folder, filename, as_attachment=False)


#   ____________________Announcement____________________

@app.route('/announcement/<int:announcement_id>')
@login_required
def view_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    class_info=announcement.class_info

    return render_template('class/announcements/class_viewannouncements.html', announcement=announcement,
                           class_info=class_info,to_tbilisi=to_tbilisi)
@app.route('/addannouncement/<int:class_id>', methods=['GET', 'POST'])
@login_required
def addannouncement(class_id):
    class_info = Class.query.get_or_404(class_id)
    form = AddAnnouncementForm()

    if form.validate_on_submit():
        name = form.name.data
        existing = Announcement.query.filter_by(class_id=class_info.id, name=name).first()
        if existing:
            flash(f'A announcement named "{name}" already exists in this class.', "danger")
            return redirect(url_for('announcements', class_id=class_info.id))


        announcement = Announcement(
            name=name,
            text=form.text.data,
            class_id=class_info.id
        )
        db.session.add(announcement)
        db.session.commit()

        flash('Announcement added successfully!', 'success')
        return redirect(url_for('announcements', class_id=class_info.id))

    return render_template('class/announcements/class_addannouncements.html', form=form, class_info=class_info)

@app.route('/announcements/<int:class_id>')
@login_required
def announcements(class_id):
    class_info = Class.query.get_or_404(class_id)
    announcement=Announcement.query.filter_by(class_id=class_id).all()
    return render_template("class/announcements/class_announcements.html", class_info=class_info, announcement=announcement)

@app.route('/delete_announcement/<int:announcement_id>', methods=['POST'])
@login_required
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    class_info = announcement.class_info

    if class_info.instructor_id != current_user.id:
        flash("You are not authorized to delete this announcement.", "danger")
        return redirect(url_for('announcements', class_id=class_info.id))

    delete_announcement(announcement)
    db.session.commit()

    flash("Announcement deleted successfully!", "success")
    return redirect(url_for('announcements', class_id=class_info.id))
@app.route('/announcement/<int:announcement_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    class_info = announcement.class_info
    form = AddAnnouncementForm(obj=announcement)

    if form.validate_on_submit():
        new_name = form.name.data.strip()
        new_text = form.text.data
        change = False

        # If name changed, check for duplicates
        if new_name != announcement.name:
            existing = Announcement.query.filter(
                Announcement.class_id == announcement.class_id,
                Announcement.name == new_name,
                Announcement.id != announcement.id
            ).first()
            if existing:
                flash(f'An announcement named "{new_name}" already exists in this class.', "danger")
                return redirect(url_for('view_announcement', announcement_id=announcement_id))

            announcement.name = new_name
            change = True


        if new_text != announcement.text:
            announcement.text = new_text
            change = True

        if change:
            announcement.updated_at = func.now()
            db.session.commit()
            flash("Announcement updated successfully.", "success")
        else:
            flash("No changes made.", "info")

        return redirect(url_for('view_announcement', announcement_id=announcement.id))

    return render_template(
        'class/announcements/class_editannouncement.html',
        form=form,
        announcement=announcement,
        class_info=class_info
    )


#   ____________________Homework____________________

@app.route('/add_homework/<int:class_id>', methods=['GET', 'POST'])
@login_required
def add_homework(class_id):
    class_info = Class.query.get_or_404(class_id)
    form = AddHomeworkForm()

    if form.validate_on_submit():
        file = form.file.data
        filename = None

        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            homework_path = os.path.join(
                app.root_path, 'static/uploads/instructors',
                str(current_user.id), 'classes', str(class_info.id), 'homeworks'
            )
            os.makedirs(homework_path, exist_ok=True)

            file_path = os.path.join(homework_path, filename)
            file.save(file_path)
        name = form.name.data
        existing = Homework.query.filter_by(class_id=class_info.id, name=name).first()
        if existing:
            flash(f'A homework named "{name}" already exists in this class.', "danger")
            return redirect(url_for('homeworks', class_id=class_info.id))

        homework = Homework(
            name=name,
            text=form.text.data,
            filename=filename,
            deadline=form.deadline.data,
            class_id=class_info.id
        )
        db.session.add(homework)
        db.session.commit()

        flash('Homework added successfully!', 'success')
        return redirect(url_for('homeworks', class_id=class_info.id))

    return render_template('class/homework/class_addhomework.html', form=form, class_info=class_info)

@app.route('/homeworks/<int:class_id>')
@login_required
def homeworks(class_id):
    class_info = Class.query.get_or_404(class_id)
    current_time = datetime.now()
    active_homeworks = Homework.query.filter(Homework.class_id == class_info.id, Homework.deadline >= current_time).all()
    return render_template('class/homework/class_homework.html', class_info=class_info, homeworks=active_homeworks)

@app.route('/homework/<int:homework_id>')
@login_required
def view_homework(homework_id):
    homework = Homework.query.get_or_404(homework_id)
    class_info = homework.class_info

    return render_template('class/homework/class_viewhomework.html', homework=homework, class_info=class_info,to_tbilisi=to_tbilisi)
@app.route('/edit_homework/<int:homework_id>', methods=['GET', 'POST'])
@login_required
def edit_homework(homework_id):
    homework = Homework.query.get_or_404(homework_id)
    class_info = homework.class_info

    if class_info.instructor_id != current_user.id:
        flash("You can’t edit homework from another instructor’s class.", "danger")
        return redirect(url_for('homeworks', class_id=homework.class_id))

    form = AddHomeworkForm(obj=homework)

    if form.validate_on_submit():
        change = False

        if form.name.data != homework.name:
            new_name = form.name.data.strip()
            existing = Material.query.filter(
                Homework.class_id == homework.class_id,
                Homework.name == new_name,
                Homework.id != homework.id
            ).first()

            if existing:
                flash(f'A homework named "{new_name}" already exists in this class.', "danger")
                return redirect(url_for('view_homework', homework_id=homework.class_id))
            homework.name = form.name.data
            change = True



        if form.text.data != homework.text:
            homework.text = form.text.data
            change = True

        if form.deadline.data != homework.deadline:
            homework.deadline = form.deadline.data
            change = True

        file = form.file.data
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"


            homework_dir = os.path.join(
                app.root_path, 'static/uploads/instructors',
                str(current_user.id), 'classes',
                str(homework.class_id), 'homeworks'
            )
            os.makedirs(homework_dir, exist_ok=True)

            file_path = os.path.join(homework_dir, filename)


            if homework.filename:
                old_path = os.path.join(homework_dir, homework.filename)
                delete_file_if_exists(old_path)

            file.save(file_path)
            homework.filename = filename
            change = True

        if change:
            homework.updated_at=func.now()
            db.session.commit()
            flash("Homework updated successfully!", "success")
        else:
            flash("No changes were made.", "info")

        return redirect(url_for('view_homework', homework_id=homework.id))

    return render_template('class/homework/class_edithomework.html', form=form, homework=homework, class_info=class_info, to_tbilisi=to_tbilisi)


@app.route('/passed_homeworks/<int:class_id>')
@login_required
def passed_homeworks(class_id):
    class_info = Class.query.get_or_404(class_id)
    current_time = datetime.now()
    expired_homeworks = Homework.query.filter(Homework.class_id == class_info.id, Homework.deadline < current_time).all()
    return render_template('class/homework/class_passedHomeworks.html', class_info=class_info, homeworks=expired_homeworks)

@app.route('/delete_homework/<int:homework_id>', methods=['POST'])
@login_required
def delete_homework(homework_id):
    homework = Homework.query.get_or_404(homework_id)
    class_info = homework.class_info

    if class_info.instructor_id != current_user.id:
        flash("You are not authorized to delete this homework.", "danger")
        return redirect(url_for('homeworks', class_id=class_info.id))

    delete_homework(homework)
    db.session.commit()

    flash("Homework deleted successfully!", "success")
    return redirect(url_for('homeworks', class_id=class_info.id))


@app.route('/download/<int:class_id>/homeworks/<filename>')
@login_required
def download_homework(class_id, filename):
    class_info = Class.query.get_or_404(class_id)

    if class_info.instructor_id != current_user.id:
        flash("You are not authorized to download this file.", "danger")
        return redirect(url_for('homeworks', class_id=class_id))

    folder = os.path.join(
        app.root_path, 'static/uploads/instructors',
        str(current_user.id), 'classes', str(class_id), 'homeworks'
    )

    return send_from_directory(folder, filename, as_attachment=True)



#   ____________________Helpers____________________
def generate_unique_class_key():
    while True:
        class_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        existing_class = Class.query.filter_by(key=class_key).first()
        if not existing_class:
            return class_key

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def delete_file_if_exists(filepath):
      if filepath and os.path.exists(filepath):
        os.remove(filepath)

def to_tbilisi(dt):
    if not dt:
        return None
    if not dt.tzinfo:
        dt = utc.localize(dt)
    return dt.astimezone(timezone("Asia/Tbilisi"))

def delete_material(material):
    if material.filename:
        file_path = os.path.join(
            app.root_path, 'static/uploads/instructors',
            str(material.class_info.instructor_id), 'classes',
            str(material.class_id), 'materials',
            material.filename
        )
        delete_file_if_exists(file_path)
    db.session.delete(material)

def delete_homework(homework):
    if homework.filename:
        file_path = os.path.join(
            app.root_path, 'static/uploads/instructors',
            str(homework.class_info.instructor_id), 'classes',
            str(homework.class_id), 'homeworks',
            homework.filename
        )
        delete_file_if_exists(file_path)
    db.session.delete(homework)

def delete_announcement(announcement):
    db.session.delete(announcement)

def delete_class(class_obj):
    base_class_dir = os.path.join(
        app.root_path, 'static/uploads/instructors',
        str(class_obj.instructor_id), 'classes', str(class_obj.id)
    )

    for material in class_obj.materials:
        delete_material(material)

    for homework in class_obj.homeworks:
        delete_homework(homework)

    for announcement in class_obj.announcements:
        delete_announcement(announcement)

    if os.path.exists(base_class_dir):
        import shutil
        shutil.rmtree(base_class_dir)

    db.session.delete(class_obj)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)











