# -*- mode: python; python-indent: 4 -*-
import ncs
import _ncs

from ncs.application import Service
from ncs.dp import Action
from collections import namedtuple
import os

from shell_commands import NetsimShell


class NetsimTool(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)

        r = self.setup_maapi()
        # Setting the default ports
        self.set_ports(r)

        devices = input.device_name if hasattr(input, 'device_name') and input.device_name else ''
        ned_id = input.ned_id if hasattr(input, 'ned_id') else None
        # default_start = r.netsim.config.start
        netsim_dir = r.netsim.config.netsim_dir

        success = ''
        error = ''

        if not netsim_dir:
            action_output(output, {'error': 'Netsim directory is not configured'})
            return

        os.environ["NETSIM_DIR"] = netsim_dir

        netsim = NetsimShell(ned_id)

        # Actions router

        if name == 'create-network':
            number = input.number
            prefix = '' if input.prefix is None else input.prefix
            response = self.create_network_action(netsim, number, prefix)
            action_output(output, response)

        if name == 'create-device':
            response = self.create_device_action(netsim, devices)
            # Sync from
            # r.devices.device[devices].sync_from.request()
            action_output(output, response)

        if name == 'delete-network':
            response = self.delete_network_action(netsim)
            action_output(output, response)

        # TODO: output for multiple devices
        if name == 'add-device':
            for device in devices:
                state = self.add_device_action(netsim, device)
                success += state['success']
                error += state['error']
            action_output(output, success, error)

        # TODO: output for multiple devices
        elif name == 'start':
            if devices:
                for device in devices:
                    state = self.start_device_action(netsim, device)
                    success += state['success']
                    error += state['error']
            else:
                state = self.start_device_action(netsim, '')
                success = state['success']
                error = state['error']

            action_output(output, success, error)

        # TODO: output for multiple devices
        elif name == 'stop':
            if devices:
                for device in devices:
                    state = self.stop_device_action(netsim, device)
                    success += state['success']
                    error += state['error']
            else:
                state = self.stop_device_action(netsim, '')
                success = state['success']
                error = state['error']

            action_output(output, success, error)

        # TODO: output for multiple devices
        elif name == 'is-alive':
            if devices:
                for device in devices:
                    state = self.alive_action(netsim, device)
                    success += state['success']
                    error += state['error']
            else:
                state = self.alive_action(netsim, '')
                success = state['success']
                error = state['error']

            action_output(output, success, error)

        elif name == 'update-network':
            ncs_run = input.ncs_run
            response = self.update_action(netsim, ncs_run)

            action_output(output, response)

    # Actions implementation

    def create_network_action(self, netsim, number, prefix):
        self.log.info('Creating new netsim network')
        error = False
        while not error:
            # Create the network
            response = netsim.create_network(number, prefix)
            if response.error:
                break
            # Init netsim device configuration
            response = netsim.init_config('')
            if response.error:
                break
            # Load init configuration to cdb
            response = netsim.load_config()
            if response.error:
                break
            break

        return response

    def create_device_action(self, netsim, device):
        self.log.info('Creating new netsim network with device ', device)
        error = False
        while not error:
            # Create the network
            response = netsim.create_device(device)
            if response.error:
                break
            # Start netsim device if configured
            # if netsim.start:
            #     response = netsim.start_device(device)
            # if not error: success = 'Network successfully created'
            # Init netsim device configuration
            response = netsim.init_config(device)
            if response.error:
                break
            # Load init configuration to cdb
            response = netsim.load_config()
            if response.error:
                break
            break

        return response

    def delete_network_action(self, netsim):
        self.log.info('Deleting {} netsim network'.format(os.environ["NETSIM_DIR"]))
        response = netsim.delete_network()

        return response

    def add_device_action(self, netsim, device):

        error = False
        while not error:
            # Add device to the network
            response = netsim.add_device(device)
            if response.error:
                break
            self.log.info('Device {} added'.format(device))
            # Start netsim device
            if netsim.start:
                response = netsim.start_device(device)
                if not response.error:
                    self.log.info('Device {} started'.format(device))
                # success = "Device {} added successfully".format(device)
            # Init netsim device configuration
            response = netsim.init_config(device)
            if response.error:
                break
            self.log.info('Device {} config initialized'.format(device))
            # Load init configuration to cdb
            response = netsim.load_config()
            if response.error:
                break
            self.log.info('Device {} loaded into cdb'.format(device))
            # Sync from
            break

        return response

    def start_device_action(self, netsim, device):
        self.log.info('Starting: ', device)
        response = netsim.start_device(device)

        return response

    def stop_device_action(self, netsim, device):
        self.log.info('Stopping: ', device)
        response = netsim.stop_device(device)

        return response

    def alive_action(self, netsim, device):
        self.log.info('Checking if {} is alive'.format(device))
        response = netsim.device_alive(device)

        return response

    def update_action(self, netsim, ncs_run):
        self.log.info('Updating netsim')

        response = netsim.update_netsim(ncs_run)
        if not response.error:
            self.log.info('No errors while updating ')
            # move response.success = "Netsim updated!"
        return response


def action_output(output, response):
    if response.error:
        output.result = False
        output.info = error + success
    else:
        output.result = True
        output.info = success


def set_ports(self, r):
    self.log.info('Setting up the ports ')
    ipc_port = str(r.netsim.config.IPC_PORT)
    netconf_ssh_port = str(r.netsim.config.NETCONF_SSH_PORT)
    netconf_tcp_port = str(r.netsim.config.NETCONF_SSH_PORT)
    snmp_port = str(r.netsim.config.SNMP_PORT)
    cli_ssh_port = str(r.netsim.config.CLI_SSH_PORT)

    os.environ["IPC_PORT"] = ipc_port
    os.environ["NETCONF_SSH_PORT"] = netconf_ssh_port
    os.environ["NETCONF_TCP_PORT"] = netconf_tcp_port
    os.environ["SNMP_PORT"] = snmp_port
    os.environ["CLI_SSH_PORT"] = cli_ssh_port


def setup_maapi(self):
    m = ncs.maapi.Maapi()
    m.start_user_session('admin', 'system', [])
    t = m.start_trans(ncs.RUNNING, ncs.READ_WRITE)
    r = ncs.maagic.get_root(t)
    return r


class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')

        self.register_action('netsim-tool', NetsimTool)

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
