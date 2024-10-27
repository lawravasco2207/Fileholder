from flask import Flask, render_template, redirect, url_for, flash, send_file
import psycopg2
import os
import io
# from flask_mail import Mail, Message
# import requests
from datetime import datetime
# from psycopg2 import sql
from urllib.parse import quote, unquote
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, FileField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Optional, Length
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import PyPDF2
from fpdf import FPDF 
# import turtle

app = Flask(__name__)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirects to login page if not logged in
login_manager.login_message_category = 'info'  # For flash messages


app.config['SECRET_KEY'] = ''
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

app.config['PROFILE_PIC_FOLDER'] = 'static/uploads/profile_pics/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['PROFILE_PIC_FOLDER'], exist_ok=True)


# make sure the uploads folder is there 
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database configuration
DB_HOST = 'ep-cool-heart-a8rml5o4.eastus2.azure.neon.tech'
DB_NAME = 'file_db'
DB_USER = 'file_db_owner'
DB_PASSWORD = '4uzXolF3yANe'
# postgresql://file_db_owner:4uzXolF3yANe@ep-cool-heart-a8rml5o4.eastus2.azure.neon.tech/file_db?sslmode=require
#  postgres://ua87miqc7vghrl:p0e017ea2ec947bbc78fac41f3bc2eaf76b31a6f7daa4b339f76af8a1b912f7e7@c9uss87s9bdb8n.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dfrm2k2kail3ne

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn


# def create_users_table():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id SERIAL PRIMARY KEY,
#             username VARCHAR(50) UNIQUE NOT NULL,
#             email VARCHAR(100) UNIQUE NOT NULL,
#             password VARCHAR(255) NOT NULL                
#         );
#     ''')
#     conn.commit()
#     cur.close()
#     conn.close()

# # call the function
# create_users_table() 


# def recreate_users_table():
#     conn = get_db_connection()
#     cur = conn.cursor()
    
#     # Step 1: Create temporary table
#     cur.execute("""
#         CREATE TABLE users_temp (
#             id SERIAL PRIMARY KEY,
#             username VARCHAR(50) UNIQUE NOT NULL,
#             email VARCHAR(100) UNIQUE NOT NULL,
#             password VARCHAR(255) NOT NULL,
#             admission_number VARCHAR(50) NOT NULL
#         );
#     """)

# #     # Step 2: Copy data from old users table
#     cur.execute("""
#         INSERT INTO users_temp (id, username, email, password, admission_number)
#         SELECT id, username, email, password, admission_number FROM users;
#     """)

#     # Step 3: Drop the old users table
#     cur.execute("DROP TABLE users;")

#     # Step 4: Rename the temporary table to users
#     cur.execute("ALTER TABLE users_temp RENAME TO users;")

#     conn.commit()
#     cur.close()
#     conn.close()

# # Call the function to recreate the users table
# recreate_users_table()

# def alter_admission_column():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("""
#          ALTER TABLE users
#          ALTER COLUMN admission_number TYPE VARCHAR(100);
#     """)
#     conn.commit()
#     cur.close()
#     conn.close()

# alter_admission_column()   



def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
        return text
    

def create_pdf(text, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(output_path)    

class User(UserMixin):
    def __init__(self, id, username, email, admission_number=None):
        self.id = id
        self.username = username
        self.email = email
        self.admission_number = admission_number

    # Additional methods can be defined if needed


# def create_notes_table():
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute('''
#         CREATE TABLE IF NOT EXISTS notes (
#             id SERIAL PRIMARY KEY,
#             user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
#             content TEXT NOT NULL,
#             timestamp TIMESTAMPTZ DEFAULT NOW()
#         );
#     ''')
#     conn.commit()
#     cur.close()
#     conn.close()

# # Call the function to create the notes table
# create_notes_table()



@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, email, admission_number FROM users WHERE id = %s', (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return User(id=user[0], username=user[1], email=user[2], admission_number=user[3])
    return None


# signup form
class SignUp(FlaskForm):
      username = StringField("Username", validators=[DataRequired()])
      email = EmailField("Email", validators=[DataRequired(), Email()])
      password = PasswordField("Password", validators=[DataRequired()])
      confirm_password = PasswordField("Confirm_Password", validators=[DataRequired(), EqualTo('password')])
      admission_number = StringField('ADM.NO', validators=[DataRequired()])
      submit = SubmitField("Create Account")

      def validate_email(self, field):
        try:
            # Validate email
            validate_email(field.data)
        except EmailNotValidError as e:
            raise ValueError(str(e))
        

      def validate_admission_number(self, field):
        admission_number = field.data
        if not (admission_number.startswith("CVL/600/S24/") or admission_number.startswith("CVL/600/M24/")):
            raise ValueError("Admission number must start with 'CVL/600/S24/' or 'CVL/600/M24/'.")
        if not admission_number[-3:].isdigit():
            raise ValueError("The last 3 characters of the admission number must be digits.")  


# login form 
class Login(FlaskForm):
      username = StringField("Username", validators=[DataRequired()])
      admission_number = StringField("ADM.NO", validators=[DataRequired()])
      password = PasswordField("Password", validators=[DataRequired()])
      submit = SubmitField("Login")


# define uploading form
class UploadForm(FlaskForm):
    pdf_file = FileField('PDF File', validators=[DataRequired()])
    submit = SubmitField('Upload') 


# notes form 
class NotesForm(FlaskForm):
    content = TextAreaField("Note", validators=[DataRequired()])
    submit = SubmitField("Save Note") 


# forms.py
class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('New Password', validators=[Optional()])
    submit = SubmitField('Update Profile')

# Profile picture upload form
class ProfilePicForm(FlaskForm):
    profile_picture = FileField('Upload Profile Picture', validators=[DataRequired()])
    submit = SubmitField('Upload Picture')

# class UploadProfilePic():
#     pic_name = FileField('Choose pic', validators=[DataRequired()])
#     submit = SubmitField('Upload')

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')    


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUp()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        admission_number = form.admission_number.data
        password = generate_password_hash(form.password.data)

        # Insert into the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email, password, admission_number) VALUES (%s, %s, %s, %s)",
                    (username, email, password, admission_number))
        conn.commit()
        cur.close()
        conn.close()

        flash('Sign up successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        admission_number = form.admission_number.data

        # Query the database for user details
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, email, password, admission_number FROM users WHERE username = %s",
            (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        # Check if the user exists, password is correct, and admission number matches
        if user and check_password_hash(user[3], password) and user[4] == admission_number:
            logged_in_user = User(id=user[0], username=user[1], email=user[2])
            login_user(logged_in_user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to dashboard or home page
        else:
            flash('Login failed. Check your username, password, and admission number.', 'danger')

    return render_template('login.html', form=form)



@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.pdf_file.data
        if file and file.filename.endswith('.pdf'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Associate the file with the current user
            save_file_to_db(file.filename, filepath, current_user.id)  # Pass current_user.id
            return redirect(url_for('dashboard'))
    return render_template('upload.html', form=form)


def save_file_to_db(filename, filepath, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    with open(filepath, 'rb') as f:
        file_data = f.read()
        print(f"Saving file of size: {len(file_data)} bytes")  # Debugging
        cur.execute('INSERT INTO pdf_files (filename, data, user_id) VALUES (%s, %s, %s)', (filename, file_data, user_id))
    conn.commit()    
    cur.close()
    conn.close()

    


@app.route('/dashboard')
@login_required
def dashboard():
    # Fetch user details and uploads
    username = current_user.username
    email = current_user.email
    admission_number = current_user.admission_number

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch user's uploads
    cur.execute('SELECT filename FROM pdf_files WHERE user_id = %s', (current_user.id,))
    uploads = cur.fetchall()

    # Fetch user's profile picture filename
    cur.execute('SELECT filename FROM profile_pics WHERE user_id = %s ORDER BY uploaded_at DESC LIMIT 1', (current_user.id,))
    profile_picture = cur.fetchone()
    profile_picture_filename = profile_picture[0] if profile_picture else None
    
    cur.close()
    conn.close()

    return render_template('dashboard.html', username=username, email=email, admission_number=admission_number, uploads=uploads, profile_picture=profile_picture_filename, quote=quote)


@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    form = NotesForm()
    if form.validate_on_submit():
        content = form.content.data
        user_id = current_user.id
        timestamp = datetime.now()

        # Insert the new note into the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO notes (user_id, content, timestamp) VALUES (%s, %s, %s)',
                    (user_id, content, timestamp))
        conn.commit()
        cur.close()
        conn.close()

        flash('Note added successfully!', 'success')
        return redirect(url_for('notes'))

    # Fetch the current user's notes from the database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, content, timestamp FROM notes WHERE user_id = %s ORDER BY timestamp DESC', (current_user.id,))
    notes = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('notes.html', form=form, notes=notes)


@app.route('/notes/delete/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Ensure the note belongs to the current user
    cur.execute('DELETE FROM notes WHERE id = %s AND user_id = %s', (note_id, current_user.id))
    if cur.rowcount == 0:
        flash('Note not found or you do not have permission to delete this note.', 'danger')
    else:
        flash('Note deleted successfully!', 'success')

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('notes'))



@app.route('/uploads/<string:encoded_filename>')
@login_required
def serve_file(encoded_filename):
    try:
        # Decode the filename to its original form
        filename = unquote(encoded_filename)
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT filename, data FROM pdf_files WHERE filename = %s AND user_id = %s', (filename, current_user.id))
        file = cur.fetchone()
        cur.close()
        conn.close()

        if file:
            filename, file_data = file
            
            # Use send_file to serve the file with correct headers
            return send_file(
                io.BytesIO(file_data), 
                download_name=filename, 
                as_attachment=True, 
                mimetype='application/pdf'
            )
        else:
            flash('File not found or permission denied.', 'danger')
            return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Error while downloading file: {str(e)}")
        flash('Something went wrong.', 'danger')
        return redirect(url_for('dashboard'))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/uploads/all')
@login_required
def all_uploads():
    conn = get_db_connection()
    cur = conn.cursor()

    # Join the pdf_files table with users table to fetch filenames and admission numbers
    cur.execute("""
        SELECT pdf_files.filename, users.admission_number 
        FROM pdf_files 
        JOIN users ON pdf_files.user_id = users.id
    """)
    uploads = cur.fetchall()
    cur.close()
    conn.close()

    # Render the 'all_uploads.html' template, passing the list of uploads
    return render_template('all_uploads.html', uploads=uploads, quote=quote)


@app.route('/uploads/delete/<string:filename>', methods=['POST'])
@login_required
def delete_upload(filename):
    conn = get_db_connection()
    cur = conn.cursor()

    # Ensure the file belongs to the current user
    cur.execute('SELECT id FROM pdf_files WHERE filename = %s AND user_id = %s', (filename, current_user.id))
    file = cur.fetchone()

    if file:
        # Delete the file record from the database
        cur.execute('DELETE FROM pdf_files WHERE filename = %s AND user_id = %s', (filename, current_user.id))
        conn.commit()

        # Optionally, delete the file from the filesystem
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        flash('File deleted successfully!', 'success')
    else:
        flash('File not found or you do not have permission to delete this file.', 'danger')

    cur.close()
    conn.close()
    
    return redirect(url_for('dashboard'))


@app.route('/update_profile', methods=['GET', 'POST'])
@login_required   
def update_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = get_db_connection()
        cur = conn.cursor()

        # Update the user's username
        cur.execute('UPDATE users SET username = %s WHERE id = %s', (username, current_user.id))

        # If a new password is provided, update it
        if password:
            hashed_password = generate_password_hash(password)
            cur.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_password, current_user.id))

        conn.commit()
        cur.close()
        conn.close()

        flash('Profile updated successfully!', 'success') 
        return redirect(url_for('dashboard'))

    # Populate the form with current user data
    form.username.data = current_user.username
    return render_template('update_profile.html', form=form)


@app.route('/upload_profile_pic', methods=['GET', 'POST'])
@login_required
def upload_profile_pic():
    form = ProfilePicForm()
    if form.validate_on_submit():
        file = form.profile_picture.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['PROFILE_PIC_FOLDER'], filename)
            file.save(filepath)

            # Save to database
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO profile_pics (user_id, filename, uploaded_at) VALUES (%s, %s, NOW())",
                    (current_user.id, filename)
                )
            conn.commit()
            conn.close()

            flash('Profile picture uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid file format or no file selected', 'danger')

    return render_template('uploaded_profile.html', form=form)



@app.route('/delete_profile_pic', methods=['POST'])
@login_required
def delete_profile_pic():
    # Query the current user profile picture from the database
    user_id = current_user.id
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM profile_pics WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    if result and result[0]:
        profile_pic = result[0]
        # Path to the file to delete
        profile_pic_path = os.path.join(app.root_path, 'static/uploads/profile_pics', secure_filename(profile_pic))
        
        try:
            # Remove the profile picture from the file system if it exists
            if os.path.exists(profile_pic_path):
                os.remove(profile_pic_path)
            
            # Update the database to remove the profile picture reference
            cursor.execute("DELETE FROM profile_pics WHERE user_id = %s", (user_id,))
            conn.commit()

            flash('Profile picture deleted successfully.', 'success')
        except Exception as e:
            flash(f"An error occurred while deleting the profile picture: {str(e)}", 'danger')
    else:
        flash('No profile picture found.', 'warning')
    
    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(debug=True)
    
