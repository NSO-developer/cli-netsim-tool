from subprocess import Popen, PIPE

"""Methods executing shell commands"""
class NetsimShell(object):
    def __init__(self, ned_id, netsim_dir, start, device_config = None):
        self.ned_id = ned_id
        self.netsim_dir = netsim_dir
        self.start = start
        self.device_config = device_config
        
    def create_network(self, number, prefix):
        command = "ncs-netsim --dir {} create-network {} {} {}".format(self.netsim_dir, self.ned_id, number, prefix)
        p = Popen(command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        
        return out, err

    def create_device(self, name):
        command = "ncs-netsim --dir {} create-device {} {}".format(self.netsim_dir, self.ned_id, name)
        p = Popen(command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        
        return out, err

    def delete_network(self):
        command = "ncs-netsim --dir {} delete-network".format(self.netsim_dir)
        p = Popen(command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        
        return out, err

    def add_device(self, name):
        command = "ncs-netsim --dir {} add-device {} {}".format(self.netsim_dir, self.ned_id, name)
        p = Popen(command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        
        return out, err
            
    def init_config(self, name):
        command = "ncs-netsim --dir {} ncs-xml-init {}".format(self.netsim_dir, name)
        p = Popen(command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        # Save config to the object
        self.device_config = out

        return out, err
        
    def load_config(self):
        command = "ncs_load -l -m"
        p = Popen(command.split(), cwd=self.netsim_dir, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate(self.device_config)

        return out, err

    def start_device(self, name):
        command = "ncs-netsim --dir {} start {}".format(self.netsim_dir, name)
        p = Popen(command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
    
        return out, err
        

    def stop_device(self, name):
        command = "ncs-netsim --dir {} stop {}".format(self.netsim_dir, name)
        p = Popen(command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()

        return out, err
    
    def device_alive(self, name):
        command = "ncs-netsim --dir {} is-alive {}".format(self.netsim_dir, name)
        p = Popen(command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()

        return out, err