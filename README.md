# System Judge Backend

## Deployment

1. Create a .env file referencing the sample file.
2. Fill the parameters into the .env file.

```sh
JWT_SECRET=""

HARBOR_HOST=""
HARBOR_USER=""
HARBOR_PASSWORD=""
HARBOR_PROJECT=""

LDAP_HOST="ldap://localhost"
LDAP_ENABLE_TLS=no
LDAP_CA_PATH=""
LDAP_USER_BASE_DN="ou=People,dc=example,dc=org"
LDAP_ADMIN_GROUP_DN="cn=admin,ou=Group,dc=example,dc=org"

WG_LISTEN_IP="localhost"

K8S_NAMESPACE="judge"
K8S_KUBE_CONFIG="/etc/kubernetes/admin.conf"
```

Make sure the parameters listed above are not empty.
If you are not using LDAP authentication, you can just skip them.

Notices:
- You have to fill your public IP which receives the wireguard traffic from internet into the `WG_LISTEN_IP` field.
- You have to create a kubernetes namespace before you use it. So as harbor project.
- DB and REDIS connection parameters should be fixed because of they are containerized and listening on the loopback interface. Hence, if it is not necessary, you may not change them.

Warnings:
- Because of the usage of Wireguard in container, we have to grant container `CAP_NET_ADMIN` capability. Make sure your network is well-designed or even isolated. Using some CNI plugin or firewall policies would be better.

