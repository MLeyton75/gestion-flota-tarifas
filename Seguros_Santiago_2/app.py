from flask import Flask, render_template, request, redirect, session, flash, jsonify
from auth import AuthSystem
from crud_model import CRUDModel
from functools import wraps
import logging

# Configurar logging más detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'seguros_santiago_secret_key_2024'
auth = AuthSystem()
crud = CRUDModel()

# Decoradores de autenticación
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning("Acceso denegado: usuario no autenticado")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def agent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 1:
            logger.warning(f"Acceso denegado a agente: user_id={session.get('user_id')}, role={session.get('role')}")
            flash('Acceso restringido a agentes', 'error')
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return decorated_function

def client_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 2:
            logger.warning(f"Acceso denegado a cliente: user_id={session.get('user_id')}, role={session.get('role')}")
            flash('Acceso restringido a clientes', 'error')
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return decorated_function

# Rutas de Autenticación
@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        logger.info(f"Intento de login - Usuario: {username}")
        
        # Validaciones básicas
        if not username or not password:
            flash('Por favor ingrese usuario y contraseña', 'error')
            return render_template('login.html')
        
        # Intentar autenticación
        user = auth.login(username, password)
        
        if user:
            # Configurar sesión
            session['user_id'] = user['id_usuario']
            session['username'] = user['nombre_usuario']
            session['role'] = user['id_rol']
            session['role_name'] = user['nombre_rol']
            
            logger.info(f"Login exitoso - Usuario: {username}, Rol: {user['nombre_rol']}, ID: {user['id_usuario']}")
            
            # Redireccionar según el rol
            if user['id_rol'] == 1:  # Agente
                flash(f'Bienvenido, {user["nombre_usuario"]}', 'success')
                return redirect('/agent/dashboard')
            elif user['id_rol'] == 2:  # Cliente
                flash(f'Bienvenido, {user["nombre_usuario"]}', 'success')
                return redirect('/client/dashboard')
            else:
                logger.error(f"Rol desconocido: {user['id_rol']}")
                flash('Rol de usuario no válido', 'error')
        else:
            logger.warning(f"Login fallido - Usuario: {username}")
            flash('Credenciales inválidas. Verifique su usuario y contraseña.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username', 'Usuario desconocido')
    session.clear()
    logger.info(f"Logout exitoso - Usuario: {username}")
    flash('Sesión cerrada correctamente', 'success')
    return redirect('/login')

# Ruta de debug para verificar usuarios (solo en desarrollo)
@app.route('/debug/users')
def debug_users():
    if app.debug:  # Solo en modo debug
        users = auth.get_all_users_debug()
        return jsonify(users)
    else:
        return jsonify({'error': 'Acceso denegado'}), 403

# Dashboard general que redirige según el rol
@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    if role == 1:  # Agente
        return redirect('/agent/dashboard')
    elif role == 2:  # Cliente
        return redirect('/client/dashboard')
    else:
        flash('Rol de usuario no válido', 'error')
        return redirect('/logout')

# Dashboard Agente
@app.route('/agent/dashboard')
@login_required
@agent_required
def agent_dashboard():
    try:
        clients = crud.get_all_clients()
        logger.info(f"Dashboard agente cargado - {len(clients) if clients else 0} clientes")
        return render_template('dashboard_agent.html', clients=clients)
    except Exception as e:
        logger.error(f"Error cargando dashboard agente: {e}")
        flash('Error cargando el dashboard', 'error')
        return redirect('/logout')

# Dashboard Cliente - CORREGIDO
@app.route('/client/dashboard')
@login_required
@client_required
def client_dashboard():
    try:
        # Primero obtener el ID del cliente asociado al usuario
        client_id_query = """
            SELECT id_cliente FROM Clientes WHERE id_usuario = %s
        """
        client_id_result = crud.db.execute_query(client_id_query, (session['user_id'],))
        
        if not client_id_result or len(client_id_result) == 0:
            logger.warning(f"No se encontró cliente para user_id: {session['user_id']}")
            flash('No se encontraron datos del cliente. Contacte al administrador.', 'error')
            return redirect('/logout')
        
        client_id = client_id_result[0]['id_cliente']
        logger.info(f"Obteniendo datos del cliente ID: {client_id}")
        
        # Usar el método existente que trae todos los datos con joins
        client = crud.get_client_by_id(client_id)
        
        if client:
            logger.info(f"Cliente encontrado: {client['nombre']} {client['apellido']}")
            return render_template('dashboard_client.html', client=client)
        else:
            logger.warning(f"No se encontraron datos del cliente para ID: {client_id}")
            flash('No se encontraron datos del cliente. Contacte al administrador.', 'error')
            return redirect('/logout')
            
    except Exception as e:
        logger.error(f"Error cargando dashboard cliente: {str(e)}")
        flash('Error cargando sus datos', 'error')
        return redirect('/logout')

# Edición limitada para cliente
@app.route('/client/edit', methods=['GET', 'POST'])
@login_required
@client_required
def client_edit_own():
    try:
        # Obtener el cliente asociado al usuario usando el método existente
        client_id_query = "SELECT id_cliente FROM Clientes WHERE id_usuario = %s"
        client_id_result = crud.db.execute_query(client_id_query, (session['user_id'],))
        
        if not client_id_result or len(client_id_result) == 0:
            logger.warning(f"Cliente no encontrado para user_id: {session['user_id']}")
            flash('No se encontraron datos del cliente', 'error')
            return redirect('/client/dashboard')
        
        client_id = client_id_result[0]['id_cliente']
        client = crud.get_client_by_id(client_id)
        
        if not client:
            logger.warning(f"Cliente no encontrado para ID: {client_id}")
            flash('No se encontraron datos del cliente', 'error')
            return redirect('/client/dashboard')
        
        if request.method == 'POST':
            try:
                # Solo permitir editar campos que el cliente puede modificar
                update_query = """
                    UPDATE Clientes SET 
                        direccion=%s, telefono=%s, correo_electronico=%s,
                        ingresos_anuales=%s, gasto_mensual=%s, carga_familiar=%s
                    WHERE id_cliente=%s
                """
                values = (
                    request.form['direccion'].strip(),
                    request.form['telefono'].strip(),
                    request.form['correo_electronico'].strip(),
                    float(request.form['ingresos_anuales']),
                    float(request.form['gasto_mensual']),
                    int(request.form['carga_familiar']),
                    client_id
                )
                
                result = crud.db.execute_query(update_query, values, fetch=False)
                
                if result:
                    logger.info(f"Cliente {client_id} actualizado exitosamente")
                    flash('Información actualizada exitosamente', 'success')
                    return redirect('/client/dashboard')
                else:
                    flash('Error al actualizar información', 'error')
                    
            except ValueError as ve:
                logger.error(f"Error de validación: {ve}")
                flash('Error: Verifique que los valores numéricos sean correctos', 'error')
            except Exception as e:
                logger.error(f"Error updating client info: {e}")
                flash('Error al procesar la solicitud', 'error')
        
        return render_template('client_edit_limited.html', client=client)
        
    except Exception as e:
        logger.error(f"Error en client_edit_own: {e}")
        flash('Error accediendo a la información', 'error')
        return redirect('/client/dashboard')

# CRUD Clientes - Agente
@app.route('/agent/clients')
@login_required
@agent_required
def client_list():
    try:
        clients = crud.get_all_clients()
        tipos_seguro = crud.get_tipos_seguro()
        clasificaciones = crud.get_clasificaciones_sistema()
        clasificaciones_agente = crud.get_clasificaciones_agente()
        
        return render_template('client_list.html', 
                             clients=clients,
                             tipos_seguro=tipos_seguro,
                             clasificaciones=clasificaciones,
                             clasificaciones_agente=clasificaciones_agente)
    except Exception as e:
        logger.error(f"Error cargando lista de clientes: {e}")
        flash('Error cargando los datos', 'error')
        return redirect('/agent/dashboard')

@app.route('/agent/client/new', methods=['GET', 'POST'])
@login_required
@agent_required
def create_client():
    if request.method == 'POST':
        try:
            client_data = {
                'codigo_cliente': request.form['codigo_cliente'],
                'id_usuario': request.form['id_usuario'],
                'rut': request.form['rut'],
                'nombre': request.form['nombre'],
                'apellido': request.form['apellido'],
                'direccion': request.form['direccion'],
                'telefono': request.form['telefono'],
                'correo_electronico': request.form['correo_electronico'],
                'genero': request.form['genero'],
                'id_tipo_seguro': request.form['id_tipo_seguro'],
                'ingresos_anuales': request.form['ingresos_anuales'],
                'gasto_mensual': request.form['gasto_mensual'],
                'carga_familiar': request.form['carga_familiar'],
                'id_clasificacion_sistema': request.form['id_clasificacion_sistema'],
                'id_clasificacion_agente': request.form['id_clasificacion_agente']
            }
            
            # Validación básica
            for key, value in client_data.items():
                if not value or str(value).strip() == '':
                    flash(f'El campo {key} es requerido', 'error')
                    return redirect('/agent/client/new')
            
            result = crud.create_client(client_data)
            if result:
                logger.info(f"Cliente creado exitosamente: {client_data['codigo_cliente']}")
                flash('Cliente creado exitosamente', 'success')
                return redirect('/agent/clients')
            else:
                flash('Error al crear cliente', 'error')
                
        except Exception as e:
            logger.error(f"Error creating client: {e}")
            flash('Error al procesar la solicitud', 'error')
    
    try:
        tipos_seguro = crud.get_tipos_seguro()
        clasificaciones = crud.get_clasificaciones_sistema()
        clasificaciones_agente = crud.get_clasificaciones_agente()
        usuarios = crud.get_all_users()
        
        return render_template('client_form.html', 
                             tipos_seguro=tipos_seguro,
                             clasificaciones=clasificaciones,
                             clasificaciones_agente=clasificaciones_agente,
                             usuarios=usuarios)
    except Exception as e:
        logger.error(f"Error cargando formulario de cliente: {e}")
        flash('Error cargando el formulario', 'error')
        return redirect('/agent/clients')

@app.route('/agent/client/edit/<int:client_id>', methods=['GET', 'POST'])
@login_required
@agent_required
def edit_client(client_id):
    client = crud.get_client_by_id(client_id)
    
    if not client:
        flash('Cliente no encontrado', 'error')
        return redirect('/agent/clients')
    
    if request.method == 'POST':
        try:
            client_data = {
                'codigo_cliente': request.form['codigo_cliente'],
                'rut': request.form['rut'],
                'nombre': request.form['nombre'],
                'apellido': request.form['apellido'],
                'direccion': request.form['direccion'],
                'telefono': request.form['telefono'],
                'correo_electronico': request.form['correo_electronico'],
                'genero': request.form['genero'],
                'id_tipo_seguro': request.form['id_tipo_seguro'],
                'ingresos_anuales': request.form['ingresos_anuales'],
                'gasto_mensual': request.form['gasto_mensual'],
                'carga_familiar': request.form['carga_familiar'],
                'id_clasificacion_sistema': request.form['id_clasificacion_sistema'],
                'id_clasificacion_agente': request.form['id_clasificacion_agente']
            }
            
            result = crud.update_client(client_id, client_data)
            if result:
                logger.info(f"Cliente {client_id} actualizado exitosamente")
                flash('Cliente actualizado exitosamente', 'success')
                return redirect('/agent/clients')
            else:
                flash('Error al actualizar cliente', 'error')
                
        except Exception as e:
            logger.error(f"Error updating client: {e}")
            flash('Error al procesar la solicitud', 'error')
    
    tipos_seguro = crud.get_tipos_seguro()
    clasificaciones = crud.get_clasificaciones_sistema()
    clasificaciones_agente = crud.get_clasificaciones_agente()
    
    return render_template('client_form.html', 
                         client=client,
                         tipos_seguro=tipos_seguro,
                         clasificaciones=clasificaciones,
                         clasificaciones_agente=clasificaciones_agente)

@app.route('/agent/client/delete/<int:client_id>', methods=['POST'])
@login_required
@agent_required
def delete_client(client_id):
    try:
        result = crud.delete_client(client_id)
        if result:
            logger.info(f"Cliente {client_id} eliminado exitosamente")
            flash('Cliente eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar cliente', 'error')
    except Exception as e:
        logger.error(f"Error deleting client: {e}")
        flash('Error al procesar la solicitud', 'error')
    
    return redirect('/agent/clients')

# Vista de detalles del cliente
@app.route('/agent/client/view/<int:client_id>')
@login_required
@agent_required
def view_client(client_id):
    client = crud.get_client_by_id(client_id)
    if not client:
        flash('Cliente no encontrado', 'error')
        return redirect('/agent/clients')
    
    return render_template('client_view.html', client=client)

# Gestión de usuarios
@app.route('/agent/users')
@login_required
@agent_required
def user_list():
    users = crud.get_all_users()
    return render_template('user_list.html', users=users)

# API para obtener datos
@app.route('/api/client/<int:client_id>')
@login_required
def get_client_api(client_id):
    client = crud.get_client_by_id(client_id)
    if client:
        return jsonify(client)
    return jsonify({'error': 'Cliente no encontrado'}), 404

if __name__ == '__main__':
    logger.info("Iniciando aplicación Seguros Santiago")
    app.run(debug=True, host='localhost', port=5000)