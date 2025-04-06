from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, date
from models import db, User, Room, Reservation, ClassGroup
from forms import LoginForm, ReservationForm
from config import Config
import secrets

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Função para gerar senhas aleatórias
def generate_password():
    return secrets.token_hex(8)

# Função para gerar o nome de usuário baseado no nome completo
def generate_username(full_name):
    names = full_name.split()
    if len(names) >= 2:
        username = f"{names[0].lower()}.{names[-1].lower()}"
    else:
        username = names[0].lower()
    return username

@app.context_processor
def inject_datetime():
    """Disponibiliza `datetime` globalmente para os templates."""
    return {'datetime': datetime}

@app.before_request
def clear_reservations_end_of_week():
    """Remove todas as reservas no domingo."""
    if date.today().weekday() == 6:  # Domingo
        Reservation.query.delete()
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            if user.password_reset_required:
                login_user(user)
                return redirect(url_for('reset_password'))
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('reserve') if not user.is_admin else url_for('admin'))
        flash('Credenciais inválidas.', 'danger')
    return render_template('login.html', form=form)

@app.route('/reset_password', methods=['GET', 'POST'])
@login_required
def reset_password():
    if not current_user.password_reset_required:
        return redirect(url_for('reserve'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        current_user.password = new_password
        current_user.password_reset_required = False
        db.session.commit()
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('reserve'))
    return render_template('reset_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    shift = request.args.get('shift', 'Matutino')
    current_day = datetime.now().strftime('%A')
    days_mapping = {
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta'
    }
    current_day_pt = days_mapping.get(current_day, 'Segunda')
    selected_day = request.args.get('day', current_day_pt)
    reservations = Reservation.query.filter_by(shift=shift, day_of_week=selected_day, approved=True).all()
    return render_template(
        'dashboard.html',
        reservations=reservations,
        shift=shift,
        days_of_week=list(days_mapping.values()),
        current_day=current_day_pt,
        selected_day=selected_day
    )

@app.route('/reserve', methods=['GET', 'POST'])
@login_required
def reserve():
    form = ReservationForm()
    form.room.choices = [(room.id, room.name) for room in Room.query.filter_by(reservations_enabled=True).all()]
    form.class_group.choices = [(c.id, c.name) for c in ClassGroup.query.all()]
    if form.validate_on_submit():
        reservation = Reservation(
            user_id=current_user.id,
            room_id=form.room.data,
            day_of_week=form.day_of_week.data,
            shift=form.shift.data,
            class_group_id=form.class_group.data,
            approved=False,
            observation=request.form.get('observation')
        )
        db.session.add(reservation)
        db.session.commit()
        flash('Reserva realizada com sucesso! Aguarde aprovação.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('reserve.html', form=form)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))

    reservations = Reservation.query.filter_by(approved=False).all()

    if request.method == 'POST':
        reservation_id = request.form.get('reservation_id')
        if reservation_id:
            reservation = Reservation.query.get_or_404(reservation_id)
            reservation.approved = True
            db.session.commit()
            flash('Reserva aprovada com sucesso!', 'success')
    return render_template('admin.html', reservations=reservations)

@app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))

    users = User.query.filter_by(is_admin=False).all()
    rooms = Room.query.all()
    class_groups = ClassGroup.query.all()

    if request.method == 'POST':
        if 'full_name' in request.form:
            full_name = request.form.get('full_name')
            if full_name:
                username = generate_username(full_name)
                password = generate_password()
                new_user = User(
                    full_name=full_name,
                    username=username,
                    password=password,
                    password_reset_required=True
                )
                db.session.add(new_user)
                db.session.commit()
                flash(f'Usuário "{username}" criado com sucesso! Senha inicial: "{password}".', 'success')

        elif 'room_name' in request.form:
            room_name = request.form.get('room_name')
            if room_name:
                new_room = Room(name=room_name)
                db.session.add(new_room)
                db.session.commit()
                flash(f'Sala "{room_name}" adicionada com sucesso!', 'success')

        elif 'class_name' in request.form:
            class_name = request.form.get('class_name')
            if class_name:
                new_class = ClassGroup(name=class_name)
                db.session.add(new_class)
                db.session.commit()
                flash(f'Turma "{class_name}" adicionada com sucesso!', 'success')

        return redirect(url_for('manage'))

    return render_template('manage.html', users=users, rooms=rooms, class_groups=class_groups)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('manage'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('manage'))

@app.route('/delete_room/<int:room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('manage'))

    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash('Sala excluída com sucesso!', 'success')
    return redirect(url_for('manage'))

@app.route('/delete_class/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('manage'))

    class_group = ClassGroup.query.get_or_404(class_id)
    db.session.delete(class_group)
    db.session.commit()
    flash('Turma excluída com sucesso!', 'success')
    return redirect(url_for('manage'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
