from subprocess import Popen, PIPE
from collections import namedtuple
import os

"""Methods executing shell commands"""


class NetsimShell(object):
    def __init__(self, ned_id, netsim_dir, device_config=None):
        self.ned_id = ned_id
        self.netsim_dir = netsim_dir
        self.device_config = device_config
        # self.cache = []
        self.result = namedtuple('Result', 'success, error')

    def create_network(self, number, prefix):
        response = self.execute(
            "ncs-netsim --dir {} create-network {} {} {}".format(self.netsim_dir, self.ned_id, number, prefix))
        return response

    def create_device(self, name):
        response = self.execute("ncs-netsim --dir {} create-device {} {}".format(self.netsim_dir, self.ned_id, name))
        return response

    def delete_network(self):
        response = self.execute("ncs-netsim --dir {} delete-network".format(self.netsim_dir))
        return response

    def add_device(self, name):
        response = self.execute("ncs-netsim --dir {} add-device {} {}".format(self.netsim_dir, self.ned_id, name))
        return response

    def init_config(self, name):
        response = self.execute("ncs-netsim --dir {} ncs-xml-init {}".format(self.netsim_dir, name))
        # Save config to the object
        if not response.error:
            self.device_config = response.success
        return response

    def load_config(self):
        response = self.execute("ncs_load -l -m", self.device_config)
        return response

    def start_device(self, name):
        response = self.execute("ncs-netsim --dir {} start {}".format(self.netsim_dir, name))
        return response

    def stop_device(self, name):
        response = self.execute("ncs-netsim --dir {} stop {}".format(self.netsim_dir, name))
        return response

    def device_alive(self, name):
        response = self.execute("ncs-netsim --dir {} is-alive {}".format(self.netsim_dir, name))
        return response

    def list_netsim(self, filter=None):
        response = self.execute("ncs-netsim --dir {} list".format(self.netsim_dir))
        return response

    def update_netsim(self, ncs_dir):
        response = self.result
        # Find all devices
        device_paths = [device.split()[5][4:] for device in self.list_netsim()[0].splitlines() if "dir=/" in device]

        for path in device_paths:
            fxs_files = [file for file in os.listdir(path) if file.endswith('.fxs')]
            for file in fxs_files:
                # wnb cache
                # if [ path for path in self.cache if file in path ]:
                response = self.execute("find -L {} -name {}".format(ncs_dir, file))
                if response.success:
                    netsim_fxs = [x for x in response.success.splitlines() if "/netsim/" + file in x][0]
                    if netsim_fxs:
                        response = self.execute("cp {} {}".format(netsim_fxs, path))
                    else:
                        response = self.result(None, "Couldn't find {} in your running directory\n"
                                                     "Check if you have the appropriate NEDs.".format(file))
                if response.error:
                    break
            if response.error:
                break

        if not response.error:
            response = self.result('Netsim updated!', None)

        return response

    def execute(self, command, stdin=None):
        p = Popen(command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate(stdin)
        return self.result(out, err)
