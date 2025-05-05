
from zoneinfo import ZoneInfo
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

import os
import random
import string
from datetime import datetime, timedelta, time
import uuid
from werkzeug.utils import secure_filename
from sqlalchemy.sql import func

app = Flask(__name__, template_folder='templates')
class Base(DeclarativeBase):
    pass

app.config['SECRET_KEY'] = 'Alohomora'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))
UPLOAD_FOLDER_HW = os.path.join(app.root_path, 'static/uploads/homeworks')
app.config['UPLOAD_FOLDER_HW'] = UPLOAD_FOLDER_HW
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads/materials')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt'}

#   ____________________Models____________________


class User(UserMixin, db.Model):
    table_name = 'users'
    id:Mapped[int] = mapped_column(db.Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    lastname: Mapped[str] = mapped_column(String(1000))
    phonenumber: Mapped[str] = mapped_column(String(1000),nullable=True)
    gender: Mapped[str] = mapped_column(String(1000))
    profile_image: Mapped[str] = mapped_column(String(1000), nullable=True)
    classes = db.relationship('Class', backref='instructor', lazy=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    @property
    def created_at_tbilisi(self):
        return self.created_at + timedelta(hours=4) if self.created_at else None

    @property
    def updated_at_tbilisi(self):
        return self.updated_at + timedelta(hours=4) if self.updated_at else None





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
        @property
        def created_at_tbilisi(self):
            return self.created_at + timedelta(hours=4) if self.created_at else None

        @property
        def updated_at_tbilisi(self):
            return self.updated_at + timedelta(hours=4) if self.updated_at else None


class Material(db.Model):
    table_name = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

    @property
    def created_at_tbilisi(self):
        return self.created_at + timedelta(hours=4) if self.created_at else None

    @property
    def updated_at_tbilisi(self):
        return self.updated_at + timedelta(hours=4) if self.updated_at else None

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

    @property
    def created_at_tbilisi(self):
        return self.created_at + timedelta(hours=4) if self.created_at else None

    @property
    def updated_at_tbilisi(self):
        return self.updated_at + timedelta(hours=4) if self.updated_at else None


class Announcement(db.Model):
    __tablename__ = 'Announcement'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    @property
    def created_at_tbilisi(self):
        return self.created_at + timedelta(hours=4) if self.created_at else None

    @property
    def updated_at_tbilisi(self):
        return self.updated_at + timedelta(hours=4) if self.updated_at else None





with app.app_context():
    db.create_all()


 #   ____________________ AUTH____________________
@app.route('/')
def home():

    if current_user.is_authenticated:
        logout_user()
    return render_template("auth/home.html")
@app.route("/login", methods=['GET', 'POST'])
def login(): # login is home page
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('instructor'))
        else:
            flash("Invalid email or password.","danger")

            return redirect(url_for("login"))

    return render_template("auth/login.html")
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email=request.form.get('email')
        existing_user=db.session.execute(db.select(User).where(User.email == email)).scalar()
        if existing_user:
            flash("An account with this email already exists.","danger")
            return redirect(url_for("register"))
        #
        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=5
        )
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            lastname=request.form.get('lastname'),
            phonenumber=request.form.get('phonenumber'),
            gender=request.form.get('gender'),
            password=hash_and_salted_password,
            profile_image="profile_placeholder.png",

        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now log in.","success")
        return redirect(url_for("login"))
    return render_template("auth/register.html")

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
    user=current_user
    if request.method == 'POST':
        name=request.form.get('name')
        email=request.form.get('email')
        phonenumber=request.form.get('phonenumber')
        profile_picture=request.files.get('profile_picture')
        change=False
        if name!= user.name:
            user.name=name
            change=True
        if email!=user.email:
            user.email=email
            change=True
        if phonenumber!=user.phonenumber:
            user.phonenumber=phonenumber
            change=True
        if profile_picture and profile_picture.filename:
                if user.profile_image and user.profile_image != "profile_placeholder.png":
                    old_path = os.path.join('static/uploads/profile_pics', user.profile_image)
                    delete_file_if_exists(old_path)

                ext = profile_picture.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4()}.{ext}"
                filepath = os.path.join('static/uploads/profile_pics', filename)

                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                profile_picture.save(filepath)
                user.profile_image = filename
                change=True
        if change:
            user.updated_at=datetime.utcnow()
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        else:
            flash("no changes were made", 'info')
        return redirect(url_for('about_instructor'))

    return render_template('user/instructor_about.html', user=current_user)

@app.route('/curriculum')
@login_required
def curriculum():

    today = datetime.today()

    start_of_week = datetime.combine((today - timedelta(days=today.weekday())).date(), datetime.min.time())

    end_of_week = datetime.combine((start_of_week + timedelta(days=6)).date(), datetime.max.time())


    classes = Class.query.filter_by(instructor_id=current_user.id).all()


    class_ids = [c.id for c in classes]





    schedule = {i: {'classes': []} for i in range(7)}
    for c in classes:
        weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index(c.day)
        schedule[weekday]['classes'].append(c)



    return render_template('user/instructor_curriculum.html', user=current_user,schedule=schedule)






# _________________Class_____________________________________

@app.route('/register_class', methods=['GET', 'POST'])
@login_required
def register_class():
    if request.method == 'POST':
        class_key = generate_unique_class_key()

        day = request.form['day']
        duration = int(request.form['duration'])

        hour = int(request.form['start_hour'])
        minute = int(request.form['start_minute'])

        start_time = datetime.strptime(f"{hour}:{minute:02d}", "%H:%M").time()
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


        base_name = request.form['name']
        name = base_name
        counter = 2
        while Class.query.filter_by(instructor_id=current_user.id, name=name).first():
            name = f"{base_name} ({counter})"
            counter += 1
        if name != base_name:
            flash(f'You already have a class named "{base_name}". This one was saved as "{name}".', "info")


        new_class = Class(
            name=name,
            subject=request.form['subject'],
            day=day,
            start_time=start_time,
            duration=duration,
            instructor_id=current_user.id,
            key=class_key
        )

        db.session.add(new_class)
        db.session.commit()

        flash("Class registered successfully!", "success")
        return redirect(url_for('class_dashboard', class_id=new_class.id))

    return render_template('class/registerClass.html')

@app.route('/edit_class/<int:class_id>', methods=['POST'])
@login_required
def edit_class(class_id):
    class_info = Class.query.get_or_404(class_id)

    if class_info.instructor_id != current_user.id:
        flash("You can't edit someone else's class.", "danger")
        return redirect(url_for('class_dashboard', class_id=class_id))

    new_name = request.form['name']
    new_subject = request.form['subject']
    new_day = request.form['day']
    new_duration = int(request.form['duration'])
    new_start_time = datetime.strptime(request.form['start_time'], "%H:%M").time()
    new_end_time = (datetime.combine(datetime.today(), new_start_time) + timedelta(minutes=new_duration)).time()


    other_classes = Class.query.filter(
        Class.instructor_id == current_user.id,
        Class.day == new_day,
        Class.id != class_id
    ).all()


    for c in other_classes:
        existing_start = c.start_time
        existing_end = (datetime.combine(datetime.today(), existing_start) + timedelta(minutes=c.duration)).time()

        if not (new_end_time <= existing_start or new_start_time >= existing_end):
            flash("This update would overlap with another class you're teaching on the same day.", "danger")
            return redirect(url_for('class_dashboard', class_id=class_id))

    if(  class_info.name ==new_name and
     class_info.subject == new_subject and
     class_info.day == new_day and
     class_info.start_time == new_start_time and
     class_info.duration == new_duration):
      flash("no changes made", "info")
      return redirect(url_for('class_dashboard', class_id=class_id))

    class_info.name = new_name
    class_info.subject = new_subject
    class_info.day = new_day
    class_info.start_time = new_start_time
    class_info.duration = new_duration

    db.session.commit()
    flash("Class updated successfully.", "success")
    return redirect(url_for('class_dashboard', class_id=class_id))


@app.route('/class_dashboard/<int:class_id>')
@login_required
def class_dashboard(class_id):
    class_info = Class.query.get_or_404(class_id)
    return render_template('class/class_about.html', class_info=class_info)

@app.route('/delete_class/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    class_to_delete = Class.query.get_or_404(class_id)

    for material in class_to_delete.materials:
        if material.filename:
            material_path = os.path.join(app.config['UPLOAD_FOLDER'], material.filename)
            delete_file_if_exists(material_path)
        db.session.delete(material)


    for homework in class_to_delete.homeworks:
        if homework.filename:
            hw_path = os.path.join(app.config['UPLOAD_FOLDER_HW'], homework.filename)
            delete_file_if_exists(hw_path)
        db.session.delete(homework)


    db.session.delete(class_to_delete)
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

    if request.method == 'POST':
        name = request.form['name']
        text = request.form['text']
        file = request.files['file']

        if not name:
            flash('Name is required.', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

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

        else:
            flash('Invalid file format.', 'danger')
            return redirect(request.url)

    return render_template('class/material/class_addmaterial.html', class_info=class_info)


@app.route('/material/<int:material_id>')
@login_required
def view_material(material_id):
    material = Material.query.get_or_404(material_id)
    class_info=material.class_info
    return render_template('class/material/class_viewmaterial.html', material=material, class_info= class_info)

@app.route('/edit_material/<int:material_id>', methods=['POST'])
@login_required
def edit_material(material_id):
    material = Material.query.get_or_404(material_id)

    # Make sure current user is the instructor for this class
    if material.class_info.instructor_id != current_user.id:
        flash("You can’t edit material from another instructor’s class.", "danger")
        return redirect(url_for('materials', class_id=material.class_id))

    new_name = request.form['name']
    new_text = request.form['text']
    file=request.files.get('file')
    change=False
    if new_name != material.name:
        material.name = new_name
        change = True

    if new_text != material.text:
        material.text = new_text
        change = True

    if file and file.filename != '' and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"


        if filename != material.filename:

            delete_file_if_exists(os.path.join(app.config['UPLOAD_FOLDER'], material.filename))


            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            material.filename = filename
            change = True

    if change:
        db.session.commit()
        flash("Material updated successfully.", "success")
    else:
        flash("No changes were made.", "info")

    return redirect(url_for('view_material', material_id=material.id))


@app.route('/download/<filename>')
@login_required
def download_material(filename):
    uploads = os.path.join(app.root_path, 'static/uploads/materials')
    return send_from_directory(uploads, filename, as_attachment=True)

@app.route('/delete_material/<int:material_id>', methods=['POST'])
@login_required
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    class_info = material.class_info

    if class_info.instructor_id != current_user.id:
        flash("You are not authorized to delete this material.", "danger")
        return redirect(url_for('materials', class_id=class_info.id))


    file_path = os.path.join(app.config['UPLOAD_FOLDER'], material.filename)
    delete_file_if_exists(file_path)

    db.session.delete(material)
    db.session.commit()
    flash("Material deleted successfully!", "success")
    return redirect(url_for('materials', class_id=class_info.id))




#   ____________________Announcement____________________

@app.route('/announcement/<int:announcement_id>')
@login_required
def view_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    class_info=announcement.class_info
    return render_template('class/announcements/class_viewannouncements.html', announcement=announcement,
                           class_info=class_info)

@app.route('/addannouncement/<int:class_id>', methods=['GET', 'POST'])
@login_required
def addannouncement(class_id):
    class_info = Class.query.get_or_404(class_id)

    if request.method == 'POST':
        name = request.form['name']
        text = request.form['text']

        if not name:
            flash('Name is required.', 'danger')
            return redirect(request.url)


        announcement = Announcement(
            name=name,
            text=text,
            class_id=class_info.id
        )
        db.session.add(announcement)
        db.session.commit()

        flash('Announcement added successfully!', 'success')
        return redirect(url_for('announcements', class_id=class_info.id))

    return render_template('class/announcements/class_addannouncements.html', class_info=class_info)

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

    db.session.delete(announcement)
    db.session.commit()
    flash("Announcement deleted successfully!", "success")
    return redirect(url_for('announcements', class_id=class_info.id))


@app.route('/announcement/<int:announcement_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)

    if request.method == 'POST':
        new_name = request.form['name']
        new_text = request.form['text']
        if new_name != announcement.name or new_text != announcement.text:
            annuncement_name=new_name
            annuncement_text=new_text
            announcement.updated_at = datetime.utcnow()
            db.session.commit()
            flash("Announcement updated successfully.", "success")
            return redirect(url_for('announcements', class_id=announcement.class_id))
        else:
            flash("No changes made", 'info')
    return redirect(url_for('announcements', class_id=announcement.class_id))




#   ____________________Homework____________________

@app.route('/add_homework/<int:class_id>', methods=['GET', 'POST'])
@login_required
def add_homework(class_id):
    class_info = Class.query.get_or_404(class_id)

    if request.method == 'POST':
        name = request.form['name']
        text = request.form['text']

        deadline_str = request.form['deadline']

        deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')  # HTML datetime-local format

        file = request.files.get('file')

        filename = None
        if file and file.filename != '' and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            file.save(os.path.join(UPLOAD_FOLDER_HW, filename))

        homework = Homework(
            name=name,
            text=text,
            filename=filename,
            deadline=deadline,
            class_id=class_info.id
        )

        db.session.add(homework)
        db.session.commit()
        # print(" hi added, name is "+ filename)
        flash('Homework added successfully!', 'success')
        return redirect(url_for('homeworks', class_id=class_info.id))

    return render_template('class/homework/class_addhomework.html', class_info=class_info)

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
    return render_template('class/homework/class_viewhomework.html', homework=homework, class_info=class_info)

@app.route('/edit_homework/<int:homework_id>', methods=['POST'])
@login_required
def edit_homework(homework_id):
    homework = Homework.query.get_or_404(homework_id)

    class_info = homework.class_info
    if class_info.instructor_id != current_user.id:
        flash("You can’t edit homework from another instructor’s class.", "danger")
        return redirect(url_for('homeworks', class_id=homework.class_id))
    new_name = request.form['name']
    new_text = request.form['text']
    new_deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%dT%H:%M')
    file = request.files.get('file')
    change=False

    if new_name != homework.name:
        homework.name = new_name
        change = True

    if new_text != homework.text:
        homework.text = new_text
        change = True

    if new_deadline != homework.deadline:
        homework.deadline = new_deadline
        change = True

    if file and file.filename != '' and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"

        # Only update if filename is different
        if filename != homework.filename:
            # Delete old file if exists
            if homework.filename:
                old_path = os.path.join(app.config['UPLOAD_FOLDER_HW'], homework.filename)
                delete_file_if_exists(old_path)

            file.save(os.path.join(app.config['UPLOAD_FOLDER_HW'], filename))
            homework.filename = filename
            change = True

    if change:
        db.session.commit()
        flash("Homework updated successfully!", "success")
    else:
        flash("No changes were made.", "info")

    return redirect(url_for('view_homework', homework_id=homework.id))





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


    file_path = os.path.join(app.root_path, 'static/uploads/homeworks', homework.filename)
    delete_file_if_exists(file_path)

    db.session.delete(homework)
    db.session.commit()
    flash("Homeworks deleted successfully!", "success")
    return redirect(url_for('homeworks', class_id=class_info.id))





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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
