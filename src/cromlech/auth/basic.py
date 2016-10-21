"""
Code forked from barrel
Copyright (C) 2006-2008 Luke Arno - http://lukearno.com/
Luke Arno can be found at http://lukearno.com/
"""

class BasicAuth(object):
    """HTTP Basic authentication middleware.
    """
    users = tuple()

    def __init__(self, users=None, session_key='session', userkey='user',
                 realm='BasicREALM'):
        """Take the app to wrap and optional settings.
        """
        if users is not None:
            self.users = users
        self.session_user_key = userkey
        self.session_key = session_key
        self.realm = realm

    def valid_user(self, username, password):
        for usr, pwd in self.users:
            if username == usr and password == pwd:
                return True
        return False

    def session_dict(self, environ):
        """Get the session for caching username.
        """
        return environ.get(self.session_key)

    def save_session(self):
        """Save out the session.

        Replace with a do-nothing if you use a package that does
        not require you to explicitly save out sessions.
        """
        session = self.session_dict()
        if session is not None:
            return session.save()

    def cache_username(self, environ, username):
        """Store the username in a session dict if found.
        
        Also populates REMOTE_USER.
        """
        environ['REMOTE_USER'] = username
        session = self.session_dict(environ)
        if session is not None:
            session[self.session_user_key] = username

    def get_cached_username(self, environ):
        """Look for the username in the session if found.
        
        Also populates REMOTE_USER if it can.
        """
        session = self.session_dict(environ)
        if session is not None:
            return session.get(self.session_user_key)
        else:
            return None

    def username_and_password(self, environ):
        """Pull the creds from the AUTHORIZAITON header.
        """
        # Should I check the auth type here?
        auth_string = environ.get('HTTP_AUTHORIZATION')
        if auth_string is None:
            return ('', '')
        else:
            return auth_string[6:].strip().decode('base64').split(':')

    def authenticate(self, environ):
        """Is this request from an authenicated user? (True or False)"""
        username, password = self.username_and_password(environ)
        if username and password:
            if self.valid_user(username, password):
                self.cache_username(environ, username)
                return True
        else:
            username = self.get_cached_username(environ)
            if username is not None:
                self.cache_username(environ, username)
                return True
            
        return False

    def not_authenticated(self, environ, start_response):
        """Respond to an unauthenticated request with a 401."""
        start_response('401 Unauthorized',
                        [('WWW-Authenticate', 'Basic realm=' + self.realm)])
        return ["401 Unauthorized: Please provide credentials."]

    def __call__(self, app):
        def basicauth_secure(environ, start_response):
            if self.authenticate(environ):
                response = app(environ, start_response)
                self.save_session()
            else:
                response = self.not_authenticated(environ, start_response)
            return response
        return basicauth_secure
