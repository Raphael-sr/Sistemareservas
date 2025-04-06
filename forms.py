from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = StringField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ReservationForm(FlaskForm):
    day_of_week = SelectField('Dia da Semana', choices=[
        ('Segunda', 'Segunda'),
        ('Terça', 'Terça'),
        ('Quarta', 'Quarta'),
        ('Quinta', 'Quinta'),
        ('Sexta', 'Sexta')
    ], validators=[DataRequired()])
    shift = SelectField('Turno', choices=[
        ('Matutino', 'Matutino'),
        ('Vespertino', 'Vespertino'),
        ('Noturno', 'Noturno')
    ], validators=[DataRequired()])
    room = SelectField('Sala', coerce=int, validators=[DataRequired()])
    class_group = SelectField('Turma', coerce=int, validators=[DataRequired()])  # Adicionado o campo de turma
    submit = SubmitField('Reservar')

class AdminForm(FlaskForm):
    username = StringField('Nome Completo do Professor', validators=[DataRequired()])
    room_name = StringField('Nome da Sala', validators=[DataRequired()])
    submit_add_user = SubmitField('Adicionar Usuário')
    submit_add_room = SubmitField('Adicionar Sala')
    submit_approve = SubmitField('Aprovar Reservas')
