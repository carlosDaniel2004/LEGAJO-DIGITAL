# RUTA: app/presentation/routes/auth_routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user
from app.application.forms import LoginForm, TwoFactorForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            usuario_service = current_app.config['USUARIO_SERVICE']
            user_id = usuario_service.attempt_login(form.username.data, form.password.data)

            if user_id:
                session['2fa_user_id'] = user_id
                session['2fa_username'] = form.username.data
                return redirect(url_for('auth.verify_2fa'))
            else:
                flash('Usuario o contraseña incorrectos.', 'danger')
        except Exception as e:
            current_app.logger.error(f"Error inesperado en login: {e}")
            flash("Ocurrió un error inesperado. Por favor, intente de nuevo.", 'danger')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/login/verify', methods=['GET', 'POST'])
def verify_2fa():
    if '2fa_user_id' not in session:
        return redirect(url_for('auth.login'))

    form = TwoFactorForm()
    if form.validate_on_submit():
        user_id = session['2fa_user_id']
        usuario_service = current_app.config['USUARIO_SERVICE']
        user = usuario_service.verify_2fa_code(user_id, form.code.data)

        if user:
            # 1. Se actualiza el último login ANTES de iniciar la sesión.
            usuario_service.update_last_login(user_id)

            # 2. Se inicia la sesión del usuario. Flask-Login volverá a cargar
            #    al usuario con los datos actualizados.
            login_user(user, remember=True)

            session.pop('2fa_user_id', None)
            session.pop('2fa_username', None)
            
            flash(f'Bienvenido de nuevo, {user.nombre_completo or user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Código de verificación incorrecto o expirado.', 'danger')

    return render_template('auth/verify_2fa.html', form=form, username=session.get('2fa_username'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado la sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))
