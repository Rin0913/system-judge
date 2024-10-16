from datetime import timezone, datetime
import jwt


class AuthService:

    def __init__(self):

        self.logger = None
        self.secret = None
        self.user_repository = None

    def init_app(self, app, jwt_secret, user_repository, logger):

        self.logger = logger
        self.secret = jwt_secret
        self.user_repository = user_repository
        app.auth_service = self

    def issue_token(self, profile, expire_time=7200):

        if self.user_repository.query(profile['uid']) is None:
            self.user_repository.create(profile['uid'])

        now = int(datetime.now(tz=timezone.utc).timestamp())
        payload = {
            "iat": now,
            "exp": now + expire_time,
        }

        payload.update(profile)
        token = jwt.encode(payload, self.secret, algorithm="HS256")
        return token

    def authenticate_token(self, payload):

        if not payload:
            raise ValueError("Token is empty")

        try:
            payload = jwt.decode(payload, self.secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as e:
            self.logger.error(f"Token has expired: {e}")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.error(f"Invalid token: {e}")
            return None

        return payload
