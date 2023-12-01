import re
import os.path

try:
    from .camera import cam_client, cam_loader
except:
    pass

from .data import dataset, imageloader


camserver_re = re.compile("^(?P<protocol>.+?)://(?P<address>.+?)(:(?P<port>\d+))?$")

def datasource(spec, *, silent=True):
    
    mo = camserver_re.match(spec)
    
    # if the regex doesn't match, it might be a directory
    if mo is None:
        if os.path.isdir(spec) == False:
            raise ValueError(f"unable to interpret datasource spec: {spec}")
        
        pipe = dataset(spec)
        pipe = imageloader(pipe)
            
        return pipe
    
    else:
        protocol = mo['protocol']
        address = mo['address']
        port = mo['port']
        
        if protocol == 'tcp':
            port = 8089 if port is None else int(port)
            url = f"tcp://{address}:{port}"
        elif protocol == 'ipc':
            if port is not None:
                raise ValueError("port not supported for IPC protocol")
            url = f"ipc://{address}"
        else:
            raise ValueError(f"unsupported protocol {protocol} - must be 'tcp' or 'ipc'")
        
        pipe = cam_client(url)
        pipe = cam_loader(pipe)
        
    return pipe
