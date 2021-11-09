import urllib


class AuthenticatedURLLib(urllib.FancyURLopener):

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def prompt_user_password(host, realm):
        return (self.username, self.password)
