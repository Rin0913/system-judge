import subprocess
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
AllowedIPs = 10.101.101.0/24
"""

class WireguardManager:

    def __init__(self, server_ip, data_dir):
        self.server_ip = server_ip
        self.data_dir = data_dir

    def init_app(self, app, server_ip, data_dir):
        self.server_ip = server_ip
        self.data_dir = data_dir
        app.wireguard_manager = self

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

    def __configure_vrf(self, ipr, profile_id, wg_interface_name):
        vrf_name = f"vrf_wg{profile_id}"
        ipr.link("add", ifname=vrf_name, kind="vrf", vrf_table=1000 + profile_id)
        vrf_index = ipr.link_lookup(ifname=vrf_name)[0]
        ipr.link("set", index=vrf_index, state="up")

        wg_index = ipr.link_lookup(ifname=wg_interface_name)[0]
        ipr.link("set", index=wg_index, master=vrf_index)

        return vrf_name

    def generate_wireguard_config(self, profile_id):
        # Keypairs generating
        server_keypair = self.__generate_wireguard_keypairs()
        user_keypair = self.__generate_wireguard_keypairs()
        judge_keypair = self.__generate_wireguard_keypairs()

        # Basic configuration
        wg_interface_name = f"wg{profile_id}"
        server_listen_port = str(20000 + int(profile_id))
        user_allowed_ips = "10.101.101.1/32, 10.89.64.0/24"

        # VPN server conf
        wg_conf_path = f"/tmp/{wg_interface_name}.conf"
        wg = WGConfig(wg_conf_path)
        wg.add_attr(None, "PrivateKey", server_keypair[0])
        wg.add_attr(None, "ListenPort", server_listen_port)
        wg.add_attr(None, "Address", "10.101.101.254/24")
        wg.add_peer(user_keypair[1])
        wg.add_attr(user_keypair[1], "AllowedIPs", user_allowed_ips)
        wg.add_peer(judge_keypair[1])
        wg.add_attr(judge_keypair[1], "AllowedIPs", "10.101.101.2/32")
        wg.write_file()

        # Judge conf
        judge_conf = PEER_CONFIG.format(peer_private_keypair=judge_keypair[0],
                                        peer_interface_ip="10.101.101.2",
                                        server_public_keypair=server_keypair[1],
                                        server_ip=self.server_ip,
                                        server_listen_port=server_listen_port)
        judge_conf_path = os.path.join(self.data_dir, f"{wg_interface_name}_judge.conf")
        with open(judge_conf_path, "w", encoding="utf-8") as f:
            f.write(judge_conf)

        self.__run_subprocess(f"wg-quick up {wg_interface_name}")

        # VRF configuration
        ipr = IPRoute()
        self.__configure_vrf(ipr, profile_id, wg_interface_name)
        ipr.close()

        # User conf
        return PEER_CONFIG.format(peer_private_keypair=user_keypair[0],
                                  peer_interface_ip="10.101.101.1",
                                  server_public_keypair=server_keypair[1],
                                  server_ip=self.server_ip,
                                  server_listen_port=server_listen_port)
