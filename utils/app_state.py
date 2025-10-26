class AppState:
    currentUser = None

class User:
    def __init__(self, login, role):
        self.login = login
        self.role = role