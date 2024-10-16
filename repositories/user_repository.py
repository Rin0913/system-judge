from models import User, WGConf


class UserRepository:

    def __init__(self, logger=None):
        self.logger = logger

    def init_app(self, app, logger):
        app.user_repository = self
        self.logger = logger

    def create(self, uid):
        user = User(name=uid)
        user.save()
        return user.id

    def __query(self, uid):
        return User.objects(name=uid).first()

    def query(self, uid):
        user = self.__query(uid)
        if user:
            return user.to_mongo().to_dict()
        return None

    def set_wireguard(self, uid, user_conf, judge_conf):
        user = self.__query(uid)
        if user:
            wg_conf = WGConf(user_conf=user_conf,
                             judge_conf=judge_conf)
            user.update(wireguard_conf=wg_conf)
            return True
        return False

    def revoke_wireguard(self, uid):
        user = self.__query(uid)
        if user:
            user.wireguard_conf = None
            user.save()
            return True
        return False
