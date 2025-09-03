from database import Database

class CRUDModel:
    def __init__(self):
        self.db = Database()

    # --------------------------
    # CLIENTES
    # --------------------------
    def get_all_clients(self):
        query = """
            SELECT 
                c.*, 
                ts.nombre_tipo_seguro, 
                cs.nombre as clasificacion_sistema, 
                ca.nombre as clasificacion_agente,
                u.nombre_usuario
            FROM Clientes c
            LEFT JOIN Tipos_Seguros ts ON c.id_tipo_seguro = ts.id_tipo_seguro
            LEFT JOIN Clasificaciones_Sistema cs ON c.id_clasificacion_sistema = cs.id_clasificacion_sistema
            LEFT JOIN Clasificaciones_Agente ca ON c.id_clasificacion_agente = ca.id_clasificacion_agente
            LEFT JOIN Usuarios u ON c.id_usuario = u.id_usuario
        """
        return self.db.execute_query(query)

    def get_client_by_id(self, client_id):
        query = """
            SELECT 
                c.*, 
                ts.nombre_tipo_seguro, 
                cs.nombre as clasificacion_sistema, 
                ca.nombre as clasificacion_agente,
                u.nombre_usuario
            FROM Clientes c
            LEFT JOIN Tipos_Seguros ts ON c.id_tipo_seguro = ts.id_tipo_seguro
            LEFT JOIN Clasificaciones_Sistema cs ON c.id_clasificacion_sistema = cs.id_clasificacion_sistema
            LEFT JOIN Clasificaciones_Agente ca ON c.id_clasificacion_agente = ca.id_clasificacion_agente
            LEFT JOIN Usuarios u ON c.id_usuario = u.id_usuario
            WHERE c.id_cliente = %s
        """
        result = self.db.execute_query(query, (client_id,))
        return result[0] if result else None

    def create_client(self, client_data):
        query = """
            INSERT INTO Clientes (
                codigo_cliente, id_usuario, rut, nombre, apellido, direccion, 
                telefono, correo_electronico, genero, id_tipo_seguro, 
                ingresos_anuales, gasto_mensual, carga_familiar, 
                id_clasificacion_sistema, id_clasificacion_agente
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            client_data['codigo_cliente'],
            client_data['id_usuario'],
            client_data['rut'],
            client_data['nombre'],
            client_data['apellido'],
            client_data['direccion'],
            client_data['telefono'],
            client_data['correo_electronico'],
            client_data['genero'],
            client_data['id_tipo_seguro'],
            client_data['ingresos_anuales'],
            client_data['gasto_mensual'],
            client_data['carga_familiar'],
            client_data['id_clasificacion_sistema'],
            client_data['id_clasificacion_agente']
        )
        return self.db.execute_query(query, values, fetch=False)

    def update_client(self, client_id, client_data):
        query = """
            UPDATE Clientes SET 
                codigo_cliente=%s, rut=%s, nombre=%s, apellido=%s, 
                direccion=%s, telefono=%s, correo_electronico=%s, genero=%s, 
                id_tipo_seguro=%s, ingresos_anuales=%s, gasto_mensual=%s, 
                carga_familiar=%s, id_clasificacion_sistema=%s, 
                id_clasificacion_agente=%s 
            WHERE id_cliente=%s
        """
        values = (
            client_data['codigo_cliente'],
            client_data['rut'],
            client_data['nombre'],
            client_data['apellido'],
            client_data['direccion'],
            client_data['telefono'],
            client_data['correo_electronico'],
            client_data['genero'],
            client_data['id_tipo_seguro'],
            client_data['ingresos_anuales'],
            client_data['gasto_mensual'],
            client_data['carga_familiar'],
            client_data['id_clasificacion_sistema'],
            client_data['id_clasificacion_agente'],
            client_id
        )
        return self.db.execute_query(query, values, fetch=False)

    def delete_client(self, client_id):
        query = "DELETE FROM Clientes WHERE id_cliente = %s"
        return self.db.execute_query(query, (client_id,), fetch=False)

    # --------------------------
    # USUARIOS
    # --------------------------
    def get_all_users(self):
        query = """
            SELECT u.*, r.nombre_rol 
            FROM Usuarios u 
            JOIN Roles r ON u.id_rol = r.id_rol
        """
        return self.db.execute_query(query)

    def create_user(self, user_data):
        query = """
            INSERT INTO Usuarios (codigo_usuario, nombre_usuario, correo_electronico, password, id_rol)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            user_data['codigo_usuario'],
            user_data['nombre_usuario'],
            user_data['correo_electronico'],
            user_data['password'],
            user_data['id_rol']
        )
        return self.db.execute_query(query, values, fetch=False)

    # --------------------------
    # DATOS MAESTROS
    # --------------------------
    def get_tipos_seguro(self):
        return self.db.execute_query("SELECT * FROM Tipos_Seguros")

    def get_clasificaciones_sistema(self):
        return self.db.execute_query("SELECT * FROM Clasificaciones_Sistema")

    def get_clasificaciones_agente(self):
        return self.db.execute_query("SELECT * FROM Clasificaciones_Agente")