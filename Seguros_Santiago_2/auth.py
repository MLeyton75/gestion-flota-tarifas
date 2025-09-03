import re
import logging
from database import Database

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthSystem:
    def __init__(self):
        self.db = Database()
    
    def validate_password(self, password):
        """Valida que la contraseña cumpla con los requisitos"""
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if not re.search(r'[A-Z]', password):
            return False, "Debe contener al menos una mayúscula"
        
        if not re.search(r'[\(\)\$\%\"\!\/&@#]', password):
            return False, "Debe contener al menos un símbolo especial ()$%\"!/&@#"
        
        return True, "Contraseña válida"
    
    def login(self, username, password):
        """Autentica un usuario con username/email y contraseña"""
        try:
            # Consulta mejorada con logging
            query = """
                SELECT u.id_usuario, u.nombre_usuario, u.correo_electronico, 
                       u.password, u.id_rol, r.nombre_rol 
                FROM Usuarios u 
                JOIN Roles r ON u.id_rol = r.id_rol 
                WHERE u.nombre_usuario = %s OR u.correo_electronico = %s
            """
            
            logger.info(f"Intentando autenticar usuario: {username}")
            
            # Ejecutar consulta
            users = self.db.execute_query(query, (username, username))
            
            # Debug: mostrar todos los usuarios encontrados
            logger.info(f"Usuarios encontrados: {len(users) if users else 0}")
            
            if users and len(users) > 0:
                user = users[0]
                logger.info(f"Usuario encontrado: {user['nombre_usuario']}, Rol: {user['nombre_rol']}")
                logger.info(f"Contraseña almacenada: {user['password']}")
                logger.info(f"Contraseña ingresada: {password}")
                
                # Verificar contraseña (comparación directa por ahora)
                if user['password'] == password:
                    logger.info(f"Login exitoso para usuario: {user['nombre_usuario']}")
                    return user
                else:
                    logger.warning(f"Contraseña incorrecta para usuario: {username}")
            else:
                logger.warning(f"Usuario no encontrado: {username}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error en login: {e}")
            return None
    
    def get_user_role(self, user_id):
        """Obtiene el rol de un usuario por ID"""
        try:
            query = "SELECT id_rol FROM Usuarios WHERE id_usuario = %s"
            result = self.db.execute_query(query, (user_id,))
            return result[0]['id_rol'] if result and len(result) > 0 else None
        except Exception as e:
            logger.error(f"Error obteniendo rol de usuario: {e}")
            return None
    
    def get_all_users_debug(self):
        """Método de debug para ver todos los usuarios"""
        try:
            query = """
                SELECT u.id_usuario, u.nombre_usuario, u.correo_electronico, 
                       u.password, u.id_rol, r.nombre_rol 
                FROM Usuarios u 
                JOIN Roles r ON u.id_rol = r.id_rol
                ORDER BY u.id_usuario
            """
            users = self.db.execute_query(query)
            
            logger.info("=== DEBUG: Todos los usuarios en la base de datos ===")
            for user in users:
                logger.info(f"ID: {user['id_usuario']}, Usuario: {user['nombre_usuario']}, "
                          f"Email: {user['correo_electronico']}, Password: {user['password']}, "
                          f"Rol: {user['nombre_rol']}")
            logger.info("=== FIN DEBUG ===")
            
            return users
            
        except Exception as e:
            logger.error(f"Error en debug de usuarios: {e}")
            return []