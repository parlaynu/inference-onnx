import re
import socket


def get_connect_url(url):
    
    if url.startswith("ipc:"):
        return url

    tcp_re = re.compile("^tcp://(?P<address>.+?):(?P<port>\d+)$")
    mo = tcp_re.match(url)
    if mo is None:
        raise ValueError(f"unable to parse {url}")
        
    address = mo['address']
    port = mo['port']
    
    if address == "0.0.0.0":
        # Below is from this https://stackoverflow.com/a/28950776
        # NOTE: calling 'connect' on a UDP socket doesn't actually communicate
        #         with the remote host, it purely sets up the local socket ready
        #         to communicate with the remote end... including determining
        #         what local address to use, which is what is needed here.
        remote_ip = '1.1.1.1'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect((remote_ip, 53))
            address = s.getsockname()[0]
        except Exception:
            address = '127.0.0.1'
        finally:
            s.close()

    url = f"tcp://{address}:{port}"
    return url
