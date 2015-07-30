from flask_wtf import Form
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class signForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    team = StringField('Team', validators=[DataRequired()])
    website = StringField('Website')
    captain = StringField('Captain')
    member1 = StringField('Member 1:', validators=[DataRequired()])
    member2 = StringField('Member 2:', validators=[DataRequired()])
    member3 = StringField('Member 3:', validators=[DataRequired()])
    member4 = StringField('Member 4:', validators=[DataRequired()])
    submit = SubmitField('Submit')

class xForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')



