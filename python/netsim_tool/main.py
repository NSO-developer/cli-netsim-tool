# -*- mode: python; python-indent: 4 -*-
import ncs
import _ncs

from ncs.application import Service
from ncs.dp import Action
import collections
import os

from shell_commands import NetsimShell


class NetsimTool(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        self.log.info('action name: ', name)
        # setting up Maapi
        r = self.setUp()

        devices = input.device_name if hasattr(input, 'device_name') and input.device_name else ''
        ned_id = input.ned_id if hasattr(input, 'ned_id') else None
        default_start = r.netsim.config.start
        netsim_dir = r.netsim.config.netsim_dir
        # default ports
        Ports = collections.namedtuple('Ports', 'IPC_PORT NETCONF_SSH_PORT NETCONF_TCP_PORT SNMP_PORT CLI_SSH_PORT' )
        if r.netsim.config.IPC_PORT is not None: Ports.IPC_PORT = r.netsim.config.IPC_PORT
        if r.netsim.config.CLI_SSH_PORT is not None: Ports.NETCONF_SSH_PORT = r.netsim.config.NETCONF_SSH_PORT
        if r.netsim.config.NETCONF_TCP_PORT is not None: Ports.NETCONF_TCP_PORT = r.netsim.config.NETCONF_TCP_PORT
        if r.netsim.config.SNMP_PORT is not None: Ports.SNMP_PORT = r.netsim.config.SNMP_PORT 
        if r.netsim.config.CLI_SSH_PORT is not None: Ports.CLI_SSH_PORT = r.netsim.config.CLI_SSH_PORT 


        success = ''
        error = ''
        
        if not netsim_dir: 
            self.action_output(output, {'error' : 'Netsim directory is not configured'})
            return
        
        netsim = NetsimShell(ned_id, netsim_dir, default_start)

        if name == 'create-network':
            number = input.number
            prefix = '' if input.prefix is None else input.prefix
            state = self.create_network_action(netsim, number, prefix)
            self.action_output(output, state['success'], state['error'])

        if name == 'create-device':
            state = self.create_device_action(netsim, devices)
            # Sync from
            # r.devices.device[devices].sync_from.request()
            self.action_output(output, state['success'], state['error'])
        
        if name == 'delete-network':
            state = self.delete_network_action(netsim)
            self.action_output(output, state['success'], state['error'])

        if name == 'add-device':
            for device in devices:        
                state = self.add_device_action(netsim, device)
                success += state['success']
                error += state['error']
            self.action_output(output, success, error)
            
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
                
            self.action_output(output, success, error)
            
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
                
            self.action_output(output, success, error)

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

            self.action_output(output, success, error)
        
        elif name == 'update-network':
            ncs_run = input.ncs_run
            state = self.update_action(netsim, ncs_run)
            success = state['success']
            error = state['error']

            self.action_output(output, success, error)

    def create_network_action(self, netsim, number, prefix):
        self.log.info('Creating new netsim network')
        error = False
        while not error:
            # Create the network
            success, error = netsim.create_network(number, prefix)
            if error: break
            # Start netsim device if configured
            # if netsim.start:
            #     s, error = netsim.start_device(device)
            # if not error: success = 'Network successfully created'
            # Init netsim device configuration
            s, error = netsim.init_config('')
            if error: break
            # Load init configuration to cdb
            s, error = netsim.load_config()
            if error: break

            break

        return {'success': success, 'error': error}

    def create_device_action(self, netsim, device):
        self.log.info('Creating new netsim network with device ', device)
        error = False
        while not error:
            # Create the network
            success, error = netsim.create_device(device)
            if error: break
            # Start netsim device if configured
            if netsim.start:
                s, error = netsim.start_device(device)
            # if not error: success = 'Network successfully created'
            # Init netsim device configuration
            s, error = netsim.init_config(device)
            if error: break
            # Load init configuration to cdb
            s, error = netsim.load_config()
            if error: break
            break

        return {'success': success, 'error': error}

    def delete_network_action(self, netsim):
        self.log.info('Deleting {} netsim network'.format(netsim.netsim_dir))
        success, error = netsim.delete_network()

        return {'success': success, 'error': error}

    def add_device_action(self, netsim, device):
        error = False
        while not error:
            # Add device to the network
            success, error = netsim.add_device(device)
            if error: break
            self.log.info('Device {} added'.format(device))
            # Start netsim device
            if netsim.start:
                s, error = netsim.start_device(device)
                if not error: 
                    self.log.info('Device {} started'.format(device))
                # success = "Device {} added successfully".format(device)
            # Init netsim device configuration
            s, error = netsim.init_config(device)
            if error: break
            self.log.info('Device {} config initialized'.format(device))
            # Load init configuration to cdb
            s, error = netsim.load_config()
            if error: break
            self.log.info('Device {} loaded into cdb'.format(device))
            # Sync from
            break

        return {'success': success, 'error': error}

    def start_device_action(self, netsim, device):
        self.log.info('Starting: ', device)
        success, error = netsim.start_device(device)

        return {'success': success, 'error': error}

    def stop_device_action(self, netsim, device):
        self.log.info('Stopping: ', device)
        success, error = netsim.stop_device(device)

        return {'success': success, 'error': error}

    def alive_action(self, netsim, device):
        self.log.info('Checking if {} is alive'.format(device))
        success, error = netsim.device_alive(device)

        return {'success': success, 'error': error}

    def update_action(self, netsim, ncs_run):
        self.log.info('Updating netsim')
        
        success, error = netsim.update_netsim(ncs_run)
        if not error:
            self.log.info('No errors while updating ')
            success = "Netsim updated!"
        return {'success': success, 'error': error}

    def action_output(self, output, success, error):
        if error:
            output.result = False
            output.info = error + success
        else:
            output.result = True
            output.info = success

    def setPorts(self, Ports):
        for name, value in Ports._asdict().iteritems():
            self.log.info('name: {}, value {}'.format(name,value))
    
    def setUp(self):
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
