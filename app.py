import os
import secrets
from flask import Flask, render_template, request, redirect, Response, send_file, flash, url_for
from flask_sqlalchemy import SQLAlchemy 
from flask_socketio import SocketIO, emit 
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_login import  LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.widgets import TextArea
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_socketio import SocketIO, emit 



app = Flask(__name__)
app.config['SECRET_KEY'] ='982c3b7bjibe0cda4d1245c92e83df279'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///filestorage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
migrate = Migrate(app, db)
manager = Manager(app)
socketio = SocketIO(app)

manager.add_command('db', MigrateCommand)


class IndexNumbers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    index_no = db.Column(db.Integer)
    is_registered = db.Column(db.Boolean, nullable=False, default=False)


class Halls(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hall = db.Column(db.String(20))

class Levels(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level = db.Column(db.String(10))




class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sector = db.Column(db.String(20))


class StudentProfile(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(120), nullable=False)
    hall = db.Column(db.String(300), nullable=False)
    level = db.Column(db.String(10), nullable=False)
    index_no = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    voted_for_president = db.Column(db.Boolean, nullable=False, default=False)
    voted_for_pro = db.Column(db.Boolean, nullable=False, default=False)
    voted_for_dinning_hall = db.Column(db.Boolean, nullable=False, default=False)
    voted_for_hall = db.Column(db.Boolean, nullable=False, default=False)
    voted_for_house = db.Column(db.Boolean, nullable=False, default=False)
    voted_for_entertainment = db.Column(db.Boolean, nullable=False, default=False)
    voted_for_library = db.Column(db.Boolean, nullable=False, default=False)
    voted_for_secretary = db.Column(db.Boolean, nullable=False, default=False)
    voted_for_environment = db.Column(db.Boolean, nullable=False, default=False)
    
class Candidates(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    candidate_name = db.Column(db.String(20), nullable=False)
    moto = db.Column(db.String(30), nullable=False)
    sector = db.Column(db.String(30), nullable=False)
    image = db.Column(db.String(120), nullable=False, default='default.jpeg')
    votes = db.Column(db.Integer, default=0)
    

class CandidatesForm(FlaskForm):
    candidate_name = StringField('Candidates Name', validators=[DataRequired()])
    moto = StringField('Candidates Moto', validators=[DataRequired()])
    sector = SelectField(u"Choose Candidate's Category", choices=[('', 'Select Category'), 
                                        ('Dinning Hall', 'Dinning Hall'), ('President', 'President'), 
                                        ('Secretary', 'Secretary'), ('PRO', 'P.R.O'), ('Library', 'Library'), 
                                        ('Entertainment', 'Entertainment'), ('Environment', 'Environment')])
    image = FileField('Candidates Profile Image', validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'JPG', 'PNG', 'JPEG'])])


    submit = SubmitField('Add New Candidate')
    ############### TO ADD VALIDATION FOR SECTOR LATER ##################



class StudentRegistration(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=5, max=40)])
    phone = StringField('Phone No.', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email() ])
    index_no = StringField('Index No.', validators=[DataRequired() ])
    level = SelectField(u'Choose Your Level', choices=[('', 'Select Your Level'), 
                                        ('Level 100', 'Level 100'), ('Level 200', 'Level 200'), 
                                        ('Level 300', 'Level 300'), ('Level 400', 'Level 400')])
    hall = SelectField(u'Choose Your Hall', choices=[('', 'Select Your Hall'), 
                                        ('Nasir Hall', 'Nasir Hall'), ('Wahab Hall', 'Wahab Hall'), 
                                        ('Mashood Hall', 'Mashood Hall')])
    
    password = PasswordField('Password', validators=[ DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                        validators=[DataRequired(), EqualTo('password')])
   
    submit = SubmitField('Submit')

    def validate_email(self, email):
        
        user = StudentProfile.query.filter_by(email=email.data).first()        
        if  user:
            raise ValidationError('That Email Is Already In Use Please Choose A Different Email' )
    
    def validate_index_no(self, index_no): 
        index_no = IndexNumbers.query.filter_by(index_no=index_no.data).first()         
        if not index_no:
            raise ValidationError('Invalid Index No.')
        elif index_no and index_no.is_registered==True:
            raise ValidationError("Index No Already Registered")
        else:
            pass
    

 
    
    def validate_hall(self, hall): 
        house = Halls.query.filter_by(hall=hall.data).first()
        if not house:
            raise ValidationError('No Hall Selected.')

    def validate_level(self, level): 
        lvl = Levels.query.filter_by(level=level.data).first()
        if not lvl:
            raise ValidationError('No Level Selected.')




class LoginForm(FlaskForm):
    index_no = StringField('Index No.', validators=[DataRequired(), Length(min=4, max=20) ])
    password = PasswordField('Password', validators=[ DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


######################################### DECORATORS ################################################



@login_manager.user_loader
def load_user(user_id):
    return StudentProfile.query.get(int(user_id))

@app.template_filter('clean_date')
def clean_date(dt):
    return dt.strftime('%d %b %Y')


def save_image(form_image):

    f_n, f_ext = os.path.splitext(form_image.filename)
    image_fn = form_image.filename
    image_path = os.path.join(app.root_path, './static/profile', image_fn) 
    form_image.save(image_path)
    return image_fn



def total_votes(category):
    total = 0
    for vote in category:
        total += vote.votes
    return total

def all_votes():
    votes = Candidates.query.all()
    allvotes = 0
    for vote in votes:
        allvotes += vote.votes
    return allvotes

bars_colors = ['bg-gradient-warning', 'bg-gradient-info', 'bg-gradient-primary', 
                'bg-gradient-success', 'bg-gradient-danger']
bg_colors = ['cyan', 'blue', 'primary', 'success', 'red', 'purple', 'orange']

####################################################################################################
def t_students():
    students = StudentProfile.query.all()
    total = 0
    for student in students:
        total += 1
    return total

total_students = t_students()



####################################################################################################





@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = StudentProfile.query.filter_by(index_no=form.index_no.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You Have Been Successfully Logged In', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful please check index No. or Password', 'danger')
    return render_template('login.html', tittle='Login', form=form, bgs=bg_colors)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/register',methods=["GET", "POST"])
def register():
    form = StudentRegistration()
    if form.validate_on_submit():
        registered = IndexNumbers.query.filter_by(index_no=form.index_no.data).first()

        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        student_profile = StudentProfile(full_name=form.full_name.data, index_no=form.index_no.data, 
                                        hall=form.hall.data, level=form.level.data, email=form.email.data, 
                                        phone=form.phone.data, password=hash_password)
        registered.is_registered=True
        db.session.add(student_profile)

        db.session.commit()
        flash('Your Account Has Been Created Successfully', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, bgs=bg_colors)

#####################################################################################################






@app.route('/new-candidate',  methods=['GET', 'POST'])
@login_required
def addcandidate():
    form = CandidatesForm()
    if form.validate_on_submit():
        image = save_image(form.image.data)
        candidate = Candidates(candidate_name=form.candidate_name.data, 
                                sector=form.sector.data, moto=form.moto.data, image=image)
        db.session.add(candidate)
        db.session.commit()
        flash('Candidate Added Successfully', 'success')
        return redirect(url_for('index'))
    return render_template('addcandidate.html', form=form, bgs=bg_colors)


@app.route('/president', methods=['GET', 'POST'])
@login_required
def president():
    if current_user.voted_for_president == True:
        flash('You have already voted for president ', 'warning')
        return redirect(url_for('index'))
    candidates = Candidates.query.filter_by(sector='President').all()
    if request.method == 'POST':
        voted_for = request.form.get('vote')
        candidate = Candidates.query.get(voted_for)
        if candidate == None:
            flash('No Vote Was Selected', 'warning')
            return redirect('')
        candidate.votes += 1
        current_user.voted_for_president = True
        #### ADD CURRENT USER VOTED FOR THIS SECTION TO TRUE #####
        db.session.commit()
        return redirect('/#president')
    return render_template('candidates.html', candidates=candidates, Category='Presidential Category')


@app.route('/dinning-hall', methods=['GET', 'POST'])
@login_required
def dinning_hall():
    if current_user.voted_for_dinning_hall == True:
        flash('You have already voted dinning-hall', 'warning')
        return redirect(url_for('index'))
    candidates = Candidates.query.filter_by(sector='Dinning Hall').all()
    if request.method == 'POST':
        voted_for = request.form.get('vote')
        candidate = Candidates.query.get(voted_for)
        if candidate == None:
            flash('No Vote Was Selected', 'warning')
            return redirect('')
        candidate.votes += 1
        current_user.voted_for_dinning_hall = True
        #### ADD CURRENT USER VOTED FOR THIS SECTION TO TRUE #####
        db.session.commit()
        return redirect('/#dinning-hall')
    return render_template('candidates.html', candidates=candidates, Category='Dinnning Hall Category')


@app.route('/secretary', methods=['GET', 'POST'])
@login_required
def secretary():
    if current_user.voted_for_secretary == True:
        flash('You have already voted secretary ', 'warning')
        return redirect(url_for('index'))
    candidates = Candidates.query.filter_by(sector='Secretary').all()
    if request.method == 'POST':
        voted_for = request.form.get('vote')
        candidate = Candidates.query.get(voted_for)
        if candidate == None:
            flash('No Vote Was Selected', 'warning')
            return redirect('')
        candidate.votes += 1
        current_user.voted_for_secretary = True
        #### ADD CURRENT USER VOTED FOR THIS SECTION TO TRUE #####
        db.session.commit()
        return redirect('/#secretary')
    return render_template('candidates.html', candidates=candidates, Category='Secretary Category')


@app.route('/pro', methods=['GET', 'POST'])
@login_required
def pro():
    if current_user.voted_for_pro == True:
        flash('You have already voted pro', 'warning')
        return redirect(url_for('index'))
    candidates = Candidates.query.filter_by(sector='PRO').all()
    if request.method == 'POST':
        voted_for = request.form.get('vote')
        candidate = Candidates.query.get(voted_for)
        if candidate == None:
            flash('No Vote Was Selected', 'warning')
            return redirect('')
        candidate.votes += 1
        current_user.voted_for_pro = True
        #### ADD CURRENT USER VOTED FOR THIS SECTION TO TRUE #####
        db.session.commit()
        return redirect('/#pro')
    return render_template('candidates.html', candidates=candidates, Category='Pro Category')


@app.route('/environment', methods=['GET', 'POST'])
@login_required
def environment():
    if current_user.voted_for_environment == True:
        flash('You have already voted environment', 'warning')
        return redirect(url_for('index'))
    candidates = Candidates.query.filter_by(sector='Environment').all()
    if request.method == 'POST':
        voted_for = request.form.get('vote')
        candidate = Candidates.query.get(voted_for)
        if candidate == None:
            flash('No Vote Was Selected', 'warning')
            return redirect('')
        candidate.votes += 1
        current_user.voted_for_environment = True
        #### ADD CURRENT USER VOTED FOR THIS SECTION TO TRUE #####
        db.session.commit()
        return redirect('/#environment')
    return render_template('candidates.html', candidates=candidates, Category='Environment Category')


@app.route('/library', methods=['GET', 'POST'])
@login_required
def library():
    if current_user.voted_for_library == True:
        flash('You have already voted library', 'warning')
        return redirect(url_for('index'))
    candidates = Candidates.query.filter_by(sector='Library').all()
    if request.method == 'POST':
        voted_for = request.form.get('vote')
        candidate = Candidates.query.get(voted_for)
        if candidate == None:
            flash('No Vote Was Selected', 'warning')
            return redirect('')
        candidate.votes += 1
        current_user.voted_for_library = True
        #### ADD CURRENT USER VOTED FOR THIS SECTION TO TRUE #####
        db.session.commit()
        return redirect('/#library')
    return render_template('candidates.html', candidates=candidates, Category='Library Category')


@app.route('/entertainment', methods=['GET', 'POST'])
@login_required
def entertainment():
    if current_user.voted_for_entertainment == True:
        flash('You have already voted entertainment', 'warning')
        return redirect(url_for('index'))
    candidates = Candidates.query.filter_by(sector='Entertainment').all()
    if request.method == 'POST':
        voted_for = request.form.get('vote')
        candidate = Candidates.query.get(voted_for)
        if candidate == None:
            flash('No Vote Was Selected', 'warning')
            return redirect('')
        candidate.votes += 1
        current_user.voted_for_entertainment = True
        #### ADD CURRENT USER VOTED FOR THIS SECTION TO TRUE #####
        db.session.commit()
        return redirect('/#entertainment')
    return render_template('candidates.html', candidates=candidates, Category='Entertainment Category')



@app.route('/hall', methods=['GET', 'POST'])
@login_required
def hall():
    if current_user.voted_for_hall == True:
        flash('You have already voted hall', 'warnig')
        return redirect(url_for('index'))
    candidates = Candidates.query.filter_by(sector=current_user.hall).all()
    if request.method == 'POST':
        voted_for = request.form.get('vote')
        candidate = Candidates.query.get(voted_for)
        if candidate == None:
            flash('No Vote Was Selected', 'warning')
            return redirect('')
        candidate.votes += 1
        current_user.voted_for_hall = True
        db.session.commit()
        #### ADD CURRENT USER VOTED FOR THIS SECTION TO TRUE #####
        return redirect('/#hall')
    return render_template('candidates.html', candidates=candidates, Category=f'{current_user.hall} Category')




@app.route('/', methods=['GET', 'POST'])
def index():
    total_vote_count = all_votes()
    secretaries = Candidates.query.filter_by(sector='Secretary').all()
    total_secretaries_votes = total_votes(secretaries)

    presidents = Candidates.query.filter_by(sector='President').all()
    total_president_votes = total_votes(presidents)

    dinning_halls = Candidates.query.filter_by(sector='Dinning Hall').all()
    total_dinning_hall_votes = total_votes(dinning_halls)

    environment = Candidates.query.filter_by(sector='Environment').all()
    total_environment_votes = total_votes(environment)

    pro_ = Candidates.query.filter_by(sector='PRO').all()
    total_pro_votes = total_votes(pro_)

    halls = Candidates.query.filter_by(sector='Hall').all()
    total_halls_votes = total_votes(halls)

    library = Candidates.query.filter_by(sector='Library').all()
    total_library_votes = total_votes(library)

    entertainment = Candidates.query.filter_by(sector='Entertainment').all()
    total_entertainment_votes = total_votes(entertainment)

    return render_template('tables.html', halls=halls, secretaries=secretaries, 
                            dinning_halls=dinning_halls, presidents=presidents, entertainment=entertainment,
                            library=library, environment=environment, pro_=pro_,
                            total_secretaries_votes=total_secretaries_votes, 
                            total_dinning_hall_votes=total_dinning_hall_votes, 
                            total_president_votes=total_president_votes, 
                            total_halls_votes=total_halls_votes, 
                            total_vote_count=total_vote_count, 
                            total_pro_votes=total_pro_votes,
                            total_library_votes=total_library_votes, 
                            total_environment_votes=total_environment_votes, 
                            total_entertainment_votes=total_entertainment_votes, 
                            colors=bars_colors, total = total_students, bgs = bg_colors)
"""

@socketio.on('vote')
def broadcast_results():
    total_vote_count = all_votes()
    secretaries = Candidates.query.filter_by(sector='Secretary').all()
    total_secretaries_votes = total_votes(secretaries)

    presidents = Candidates.query.filter_by(sector='President').all()
    total_president_votes = total_votes(presidents)

    dinning_halls = Candidates.query.filter_by(sector='Dinning Hall').all()
    total_dinning_hall_votes = total_votes(dinning_halls)

    environment = Candidates.query.filter_by(sector='Environment').all()
    total_environment_votes = total_votes(environment)

    pro_ = Candidates.query.filter_by(sector='PRO').all()
    total_pro_votes = total_votes(pro_)

    halls = Candidates.query.filter_by(sector='Hall').all()
    total_halls_votes = total_votes(halls)

    library = Candidates.query.filter_by(sector='Library').all()
    total_library_votes = total_votes(library)

    entertainment = Candidates.query.filter_by(sector='Entertainment').all()
    total_entertainment_votes = total_votes(entertainment)

    
    print('\n \n \n  working \n \n \n')

    emit('vote_results', { "halls" : halls, "secretaries" :secretaries, 
                            "dinning_halls" : dinning_halls, "presidents":presidents, "entertainment":entertainment,
                            "library":library, "environment":environment, "pro_":pro_,
                            "total_secretaries_votes":total_secretaries_votes, 
                            "total_dinning_hall_votes":total_dinning_hall_votes, 
                            "total_president_votes":total_president_votes, 
                            "total_halls_votes":total_halls_votes, 
                            "total_vote_count":total_vote_count, 
                            "total_pro_votes":total_pro_votes,
                            "total_library_votes":total_library_votes, 
                            "total_environment_votes":total_environment_votes, 
                            "total_entertainment_votes":total_entertainment_votes, 
                            "colors":bars_colors, "total" : total_students}, broadcast=True)


"""

@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)





























@app.route('/num')
def num():
    with open('./creds/numbers.txt', 'r') as f:
        index_numbers = f.readlines()
        for i in index_numbers:
            number = IndexNumbers(index_no=i)
            db.session.add(number)
            db.session.commit()
    with open('./creds/category.txt', 'r') as f:
        index_numbers = f.readlines()
        for i in index_numbers:
            item = Categories(sector=i)
            db.session.add(item)
            db.session.commit()
    with open('./creds/levels.txt', 'r') as f:
        index_numbers = f.readlines()
        for i in index_numbers:
            lvl = Levels(level=i)
            db.session.add(lvl)
            db.session.commit()
    with open('./creds/halls.txt', 'r') as f:
        index_numbers = f.readlines()
        for i in index_numbers:
            hll = Halls(hall=i)
            db.session.add(hll)
            db.session.commit()
    return redirect('/')
            





if __name__=="__main__":
    socketio.run(app, debug=True)
    #app.run(debug=True)
    #manager.run()