from subprocess import Popen, PIPE
import os

"""Methods executing shell commands"""
class NetsimShell(object):
    def __init__(self, ned_id, netsim_dir, start, device_config = None):
        self.ned_id = ned_id
        self.netsim_dir = netsim_dir
        self.start = start
        self.device_config = device_config
        self.cache = []

        
    def create_network(self, number, prefix):
        out, err = self.execute("ncs-netsim --dir {} create-network {} {} {}".format(self.netsim_dir, self.ned_id, number, prefix))
        
        return out, err

    def create_device(self, name):
        out, err = self.execute("ncs-netsim --dir {} create-device {} {}".format(self.netsim_dir, self.ned_id, name))
        
        return out, err

    def delete_network(self):
        out, err = self.execute("ncs-netsim --dir {} delete-network".format(self.netsim_dir))

        return out, err

    def add_device(self, name):
        out, err = self.execute("ncs-netsim --dir {} add-device {} {}".format(self.netsim_dir, self.ned_id, name))
        
        return out, err
            
    def init_config(self, name):
        out, err = self.execute("ncs-netsim --dir {} ncs-xml-init {}".format(self.netsim_dir, name))
        # Save config to the object
        self.device_config = out

        return out, err
        
    def load_config(self):
        self.execute("ncs_load -l -m")

        return out, err

    def start_device(self, name):
        self.execute("ncs-netsim --dir {} start {}".format(self.netsim_dir, name))
    
        return out, err
        

    def stop_device(self, name):
        self.execute("ncs-netsim --dir {} stop {}".format(self.netsim_dir, name))
        
        return out, err
    
    def device_alive(self, name):
        self.execute("ncs-netsim --dir {} is-alive {}".format(self.netsim_dir, name))
        
        return out, err

    def update_netsim(self, ncs_dir):
        # Find out all devices
        # return [device.split()[5][4:] for device in self.list_netsim()[0].splitlines() if "dir=/" in device]
        device_paths = [device.split()[5][4:] for device in self.list_netsim()[0].splitlines() if "dir=/" in device]

        for path in device_paths:
            fxs = [ file for file in os.listdir(path) if file.endswith('.fxs')]
            for file in fxs:
                # wnb cache
                # if [ path for path in self.cache if file in path ]:
                out, err = self.execute("find {} -name {}".format(ncs_dir, file))
                if out:
                    out, err = self.execute("cp {} {}".format(out, path))
                if err: break
            if err: break

        return out, err

    def list_netsim(self, filter=None):
        out, err = self.execute("ncs-netsim --dir {} list".format(self.netsim_dir))
        
        return out, err

    def execute(self, command):
        p = Popen(command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out, err

