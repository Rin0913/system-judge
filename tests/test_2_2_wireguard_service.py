import logging
from types import SimpleNamespace

from services import WireguardService

wireguard_service = WireguardService()
wireguard_service.init_app(SimpleNamespace(), "localhost", logging)

def test_generate_conf():
    # Listen on a normal port
    assert wireguard_service.generate_config(20000, if_up=False) is not None
    # Listen on a privileged port
    assert wireguard_service.generate_config(-19999, if_up=False) is None
