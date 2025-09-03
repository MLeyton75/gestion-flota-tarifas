from database import Database

class UserModel:
    def __init__(self):
        self.db = Database()
    
    def get_user_by_id(self, user_id):
        query = "SELECT * FROM Usuarios WHERE id_usuario = %s"
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_user_by_username(self, username):
        query = "SELECT * FROM Usuarios WHERE nombre_usuario = %s"
        result = self.db.execute_query(query, (username,))
        return result[0] if result else None
    
    def get_user_by_email(self, email):
        query = "SELECT * FROM Usuarios WHERE correo_electronico = %s"
        result = self.db.execute_query(query, (email,))
        return result[0] if result else None