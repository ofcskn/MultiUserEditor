class AppSession:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppSession, cls).__new__(cls)
            cls._instance.username = None
        return cls._instance

    def set_user(self, username):
        self.username = username

    def get_user(self):
        return self.username
