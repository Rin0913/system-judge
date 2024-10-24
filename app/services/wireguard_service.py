import subprocess
import socket
import os
from pyroute2 import IPRoute
from wgconfig import WGConfig

PEER_CONFIG = """
[Interface]
PrivateKey = {peer_private_keypair}
Address = {peer_interface_ip}/32
DNS = 8.8.8.8

[Peer]
PublicKey = {server_public_keypair}
Endpoint = {server_ip}:{server_listen_port}
AllowedIPs = 10.101.101.0/24{allow_ips}
PersistentKeepalive = 3
""".strip()

class WireguardService:

    def __init__(self, server_ip=None, logger=None):
        self.server_ip = server_ip
        self.logger = logger

    def init_app(self, app, server_ip, logger):
        app.wireguard_service = self
        self.server_ip = server_ip
        self.logger = logger

    def __check_port(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.bind(('0.0.0.0', int(port)))
                return True
            except socket.error:
                return False

    def __run_subprocess(self, command):
        return (
            subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE)
            .stdout.decode()
            .strip()
        )

    def __generate_wireguard_keypairs(self):
        private_keypair = self.__run_subprocess("wg genkey")
        public_keypair = self.__run_subprocess(f"echo {private_keypair} | wg pubkey")
        return private_keypair, public_keypair

    def __configure_vrf(self, profile_id, wg_interface_name): # pragma: no cover

        vrf_name = f"vrf_wg{profile_id}"

        ipr = IPRoute()
        ipr.link("add", ifname=vrf_name, kind="vrf", vrf_table=1000 + profile_id)
        vrf_index = ipr.link_lookup(ifname=vrf_name)[0]
        ipr.link("set", index=vrf_index, state="up")
        wg_index = ipr.link_lookup(ifname=wg_interface_name)[0]
        ipr.link("set", index=wg_index, master=vrf_index)
        ipr.route("add", dst="10.89.64.0/24", oif=wg_index, table=1000 + profile_id)
        ipr.close()

        return vrf_name

    def revoke_config(self, profile_id):
        vrf_name = f"vrf_wg{profile_id}"
        wg_interface_name = f"wg{profile_id}"
        wg_conf_path = f"/etc/wireguard/{wg_interface_name}.conf"

        ipr = IPRoute()
        try:
            vrf_index = ipr.link_lookup(ifname=vrf_name)[0]
            wg_index = ipr.link_lookup(ifname=wg_interface_name)[0]
            ipr.link("set", index=wg_index, master=0)
            ipr.link("del", index=vrf_index)
            self.logger.info(self.__run_subprocess(f"wg-quick down {wg_interface_name}"))
            os.remove(wg_conf_path)
        except Exception as e: # pylint: disable=broad-except
            self.logger.error(e)
        finally:
            ipr.close()

    def set_up(self, profile_id):
        try:
            wg_interface_name = f"wg{profile_id}"
            self.logger.info(self.__run_subprocess(f"wg-quick up {wg_interface_name}"))
            self.__configure_vrf(profile_id, wg_interface_name)
        except Exception as e:# pylint: disable=broad-except
            self.logger.warning(e)

    def generate_config(self, profile_id, if_up=True):
        # Keypairs generating
        server_keypair = self.__generate_wireguard_keypairs()
        user_keypair = self.__generate_wireguard_keypairs()
        judge_keypair = self.__generate_wireguard_keypairs()

        # Basic configuration
        wg_interface_name = f"wg{profile_id}"
        server_listen_port = str(20000 + int(profile_id))
        user_allowed_ips = "10.101.101.1/32, 10.89.64.0/24"

        # Check if the port is idle
        if not self.__check_port(server_listen_port):
            return None

        # VPN server conf
        wg_conf_path = f"/etc/wireguard/{wg_interface_name}.conf"
        wg = WGConfig(wg_conf_path)
        wg.add_attr(None, "PrivateKey", server_keypair[0])
        wg.add_attr(None, "ListenPort", server_listen_port)
        wg.add_attr(None, "Address", "10.101.101.254/24")
        wg.add_peer(user_keypair[1])
        wg.add_attr(user_keypair[1], "AllowedIPs", user_allowed_ips)
        wg.add_peer(judge_keypair[1])
        wg.add_attr(judge_keypair[1], "AllowedIPs", "10.101.101.2/32")

        # Really create the interface and make them up
        if if_up: # pragma: no cover
            wg.write_file()
            print("write to files")
            self.logger.warning("write to files")
            self.logger.info(self.__run_subprocess(f"wg-quick up {wg_interface_name}"))
            self.__configure_vrf(profile_id, wg_interface_name)

        # Store user conf and judge conf into DB
        user_conf  = PEER_CONFIG.format(peer_private_keypair=user_keypair[0],
                                        peer_interface_ip="10.101.101.1",
                                        server_public_keypair=server_keypair[1],
                                        server_ip=self.server_ip,
                                        server_listen_port=server_listen_port,
                                        allow_ips="")

        judge_conf = PEER_CONFIG.format(peer_private_keypair=judge_keypair[0],
                                        peer_interface_ip="10.101.101.2",
                                        server_public_keypair=server_keypair[1],
                                        server_ip=self.server_ip,
                                        server_listen_port=server_listen_port,
                                        allow_ips=", 10.89.64.0/24")
        return (user_conf, judge_conf)
