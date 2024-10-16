import ssl
from ldap3 import Server, Connection, SAFE_SYNC, Tls
from ldap3.utils.dn import safe_dn

class LdapService:

    def __init__(self):
        self.server = None
        self.enable_tls = None
        self.user_base_dn = None
        self.admin_group_dn = None

    def init_app(self, app, config):
        app.ldap_service = self
        self.enable_tls = config.get('LDAP_ENABLE_TLS')
        self.user_base_dn = config.get('LDAP_USER_BASE_DN')
        self.admin_group_dn = config.get('LDAP_ADMIN_GROUP_DN')
        if self.enable_tls:
            tls_configuration = Tls(
                ca_certs_file = config.get('LDAP_CA_PATH'),
                validate=ssl.CERT_OPTIONAL,
                version=ssl.PROTOCOL_TLSv1_2
            )

            self.server = Server(config.get('LDAP_HOST'),
                                 use_ssl=False,
                                 tls=tls_configuration)
        else:
            self.server = Server(config.get('LDAP_HOST'))

    def authenticate(self, username, password):
        profile = {}
        user_dn = safe_dn((f'uid={username}', self.user_base_dn))

        # Basic authentication
        conn = Connection(self.server,
                          user_dn,
                          password,
                          client_strategy=SAFE_SYNC,
                          auto_bind=False)
        if self.enable_tls:
            conn.start_tls()
        if conn.bind():
            profile['username'] = username
            profile['role'] = 'user'
        else:
            return None
        if conn.extend.standard.who_am_i() != f"dn:{user_dn}":
            return None

        # Check admin
        _, _, response, _ = conn.search(self.admin_group_dn,
                                        '(objectClass=*)',
                                        attributes=['gidNumber'])
        admin_gid = None
        if len(response):
            admin_gid = response[0]['attributes']['gidNumber']
        _, _, response, _ = conn.search(user_dn,
                                        '(objectClass=*)',
                                        attributes=['gidNumber'])
        if len(response) and admin_gid == response[0]['attributes']['gidNumber']:
            profile['role'] = 'admin'

        return profile
