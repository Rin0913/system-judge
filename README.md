# System Judge Backend

## Prerequisite

Network:
```sh
iptables -A FORWARD -j ACCEPT
iptables -t nat -A POSTROUTING -j MASQUERADE
sysctl -w net.ipv4.ip_forward=1
```

Tools:
- docker
- wireguard: `apt install wireguard`
- make: `apt install make`

## Deployment

1. Create a .env file referencing the sample file.
2. Fill the parameters, and add the following line into the .env file.
    ```sh
    RUNTIME_CONFIG="Production"
    ```
3. Execute the following command:
    ```
    venv/bin/gunicorn --bind localhost:8000 main:app
    ```

Make sure the parameters listed above are not empty.
If you are not using LDAP authentication, you can just skip them.

Notices:
- You have to fill your public IP which receives the wireguard traffic from internet into the `WG_LISTEN_IP` field.
- You have to create a kubernetes namespace before you use it. So as harbor project.
- DB and REDIS connection parameters should be fixed because they are containerized and listening on the loopback interface. Hence, if it is not necessary, you may not change them.

Warnings:
- Because of the usage of Wireguard in container, we have to grant container `CAP_NET_ADMIN` capability. Make sure your network is well-designed or even isolated. Using some CNI plugin or firewall policies would be better.
- Make sure your firewalls of judge server is well-configured, because traffic forwarding and NAT are enabled by default.

## Also See

- [System Judge Proposal](https://sandb0x.tw/b/system-judge.md)
