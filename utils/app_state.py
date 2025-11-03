class AppState:
    currentUser = None

class User:
    def __init__(self, login:str, role:int, warehouses:list):
        self.login:str = login
        self.role:int = role
        self.warehouses:list = warehouses