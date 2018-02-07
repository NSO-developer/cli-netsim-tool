# -*- mode: python; python-indent: 4 -*-
import _ncs
import ncs
import os
from collections import namedtuple
from ncs.application import Service
from ncs.dp import Action
from shell_commands import NetsimShell


class NetsimTool(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        success = ''
        error = ''
        message = namedtuple('Message', 'success, error')
        r = setup_maapi()
        set_ports(r)

        devices = input.device_name if hasattr(input, 'device_name') and input.device_name else ''
        ned_id = input.ned_id if hasattr(input, 'ned_id') else None
        netsim_dir = r.netsim.config.netsim_dir
        # default_start = r.netsim.config.start

        netsim = NetsimShell(ned_id, netsim_dir)

        # Actions router

        if name == 'create-network':
            number = input.number
            prefix = '' if input.prefix is None else input.prefix
            response = self.create_network_action(netsim, number, prefix)
            action_output(output, response)

        if name == 'create-device':
            response = self.create_device_action(netsim, devices)
            action_output(output, response)

        if name == 'delete-network':
            response = self.delete_network_action(netsim)
            action_output(output, response)

        if name == 'add-device':
            for device in devices:
                result = self.add_device_action(netsim, device)
                success += result.success
                error += result.error
            action_output(output, message(success, error))

        # TODO: output for multiple devices
        elif name == 'start':
            if devices:
                for device in devices:
                    result = self.start_device_action(netsim, device)
                    success += result.success
                    error += result.error
            else:
                result = self.start_device_action(netsim, '')
                success += result.success
                error += result.error

            action_output(output, message(success, error))

        elif name == 'stop':
            if devices:
                for device in devices:
                    result = self.stop_device_action(netsim, device)
                    success += result.success
                    error += result.error
            else:
                result = self.stop_device_action(netsim, '')
                success += result.success
                error += result.error

            action_output(output, message(success, error))

        elif name == 'is-alive':
            if devices:
                for device in devices:
                    state = self.alive_action(netsim, device)
                    success += state.success
                    error += state.error
            else:
                state = self.alive_action(netsim, '')
                success = state.success
                error = state.error

            action_output(output, message(success, error))

        elif name == 'list':
            response = self.list_action(netsim)
            action_output(output, response)

        elif name == 'load':
            response = self.load_action(netsim)
            success = "Netsim devices loaded!"
            action_output(output, message(success, response.error))

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
            create_response = netsim.create_network(number, prefix)
            if create_response.error:
                break
            # Init netsim device configuration
            init_response = netsim.init_config('')
            if init_response.error:
                break
            # Load init configuration to cdb
            load_response = netsim.load_config()
            if load_response.error:
                break

            break

        return create_response

    def create_device_action(self, netsim, device):
        self.log.info('Creating new netsim network with device ', device)
        error = False
        while not error:
            # Create the network
            create_response = netsim.create_device(device)

            if create_response.error:
                break
            # Start netsim device if configured
            # if netsim.start:
            #     response = netsim.start_device(device)
            # if not error: success = 'Network successfully created'
            # Init netsim device configuration
            init_response = netsim.init_config(device)
            if init_response.error:
                break
            # Load init configuration to cdb
            load_response = netsim.load_config()
            if load_response.error:
                break
            break

        return create_response

    def delete_network_action(self, netsim):
        self.log.info('Deleting {} netsim network'.format(os.environ["NETSIM_DIR"]))
        response = netsim.delete_network()

        return response

    def add_device_action(self, netsim, device):
        self.log.info('Adding device {} to the network'.format(device))
        error = False
        while not error:
            # Add device to the network
            add_response = netsim.add_device(device)
            if add_response.error:
                break
            # Start netsim device
            # if netsim.start:
            #     response = netsim.start_device(device)
            #     if not response.error:
            #         self.log.info('Device {} started'.format(device))

            # Init netsim device configuration
            init_response = netsim.init_config(device)
            if init_response.error:
                break
            # Load init configuration to cdb
            load_response = netsim.load_config()
            if load_response.error:
                break

            break

        return add_response

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

    def list_action(self, netsim):
        self.log.info('Listing netsim devices')
        response = netsim.list_netsim()

        return response

    def load_action(self, netsim):
        self.log.info('Loading netsim devices')

        response = netsim.init_config('')
        response = netsim.load_config()

        return response

    def update_action(self, netsim, ncs_run):
        self.log.info('Updating netsim')
        response = netsim.update_netsim(ncs_run)

        return response


def action_output(output, response):
    if response.error:
        output.result = False
        output.info = response.error
    else:
        output.result = True
        output.info = response.success


def set_ports(r):
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

    netsim_dir = r.netsim.config.netsim_dir
    os.environ["NETSIM_DIR"] = netsim_dir


def setup_maapi():
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
