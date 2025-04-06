from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)  # Nome de usuário único
    full_name = db.Column(db.String(100), nullable=False)  # Nome completo do professor
    password = db.Column(db.String(100), nullable=False)  # Senha
    password_reset_required = db.Column(db.Boolean, default=True)  # Exige redefinição de senha no primeiro login
    is_admin = db.Column(db.Boolean, default=False)  # Define se o usuário é administrador


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # Nome da sala
    reservations_enabled = db.Column(db.Boolean, default=True)  # Estado das reservas (aberto ou bloqueado)


class ClassGroup(db.Model):  # Nova tabela para gerenciar turmas
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # Nome da turma


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ID do professor
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)  # ID da sala
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), nullable=True)  # ID da turma
    day_of_week = db.Column(db.String(20), nullable=False)  # Dia da semana
    shift = db.Column(db.String(20), nullable=False)  # Turno (Matutino, Vespertino, Noturno)
    observation = db.Column(db.Text, nullable=True)  # Observações opcionais, visíveis apenas para o admin
    approved = db.Column(db.Boolean, default=False)  # Indica se a reserva foi aprovada

    user = db.relationship('User', backref='reservations')  # Relacionamento com User
    room = db.relationship('Room', backref='reservations')  # Relacionamento com Room
    class_group = db.relationship('ClassGroup', backref='reservations')  # Relacionamento com ClassGroup
