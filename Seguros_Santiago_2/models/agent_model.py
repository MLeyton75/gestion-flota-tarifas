from database import Database

class AgentModel:
    def __init__(self):
        self.db = Database()
    
    def get_agent_by_user_id(self, user_id):
        query = "SELECT * FROM Agentes WHERE id_usuario = %s"
        result = self.db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    def get_agent_by_id(self, agent_id):
        query = "SELECT * FROM Agentes WHERE id_agente = %s"
        result = self.db.execute_query(query, (agent_id,))
        return result[0] if result else None