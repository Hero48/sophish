from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.widgets import TextArea
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError









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
