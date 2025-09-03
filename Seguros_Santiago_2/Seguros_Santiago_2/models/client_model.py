from database import Database

class ClientModel:
    def __init__(self):
        self.db = Database()
    
    # Obtener todos los clientes
    def get_all_clients(self):
        query = "SELECT * FROM Clientes"
        return self.db.execute_query(query)
    
    # Obtener un cliente por ID específico (opcional)
    def get_client_by_id(self, client_id):
        query = "SELECT * FROM Clientes WHERE id_cliente = %s"
        result = self.db.execute_query(query, (client_id,))
        return result[0] if result else None
