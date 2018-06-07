## netsim-tool
A package wrapping netsim commands. Available **only for NSO local-install**. Tested on Ubuntu 16.04.

## Purpose
netsim-tool enables you to easily add new netsim networks, multiple devices to existing networks and most of other commands
otherwise available with _ncs-netsim_ command. List of available commands below.
* create-network
* create-device
* delete-network
* add-device
* start
* stop
* is-alive
* list
* load
* update-network

## Documentation
Apart from this README, please refer to the python code and associated YANG file.

## Dependencies
* NSO 4.3.6+ Local installation (Probably works on older versions aswell but not tested)
* Python 2.7+ or 3+
* Python Popen module
## Build instructions
make -C <running dir>/packages/netsim-tool/src clean all

## Usage examples
### config
User can configure default ports of running netsim processes and netsim-dir, which represents the folder where netsim network and devices are created.
In this way it's easy to switch between multiple netsim networks. Users should specify absolute path for a directory where they want to create the network.
Default value is _/netsim-lab_.
```admin@ncs(config)# netsim config netsim-dir /ios-netsim-lab```
### create-device
New networks can be created by using _create-network_ or _create-device_ actions. Both will create new network and load devices to NSO cdb.
```admin@ncs# netsim create-device device-name R1 ned-id cisco-ios```
### add-device
Users can add one or multiple devices to existing networks. This action also creates devices and loads them to NSO cdb.
```netsim add-device device-name [ R2 R3 R4 ] ned-id cisco-ios```
### start
Netsim devices can be started or stopped using start action. If user provides list of devices then only those will be started. If he skips the list all of netsim devices will be started.
```admin@ncs(config)# netsim start device-name [ R1 R3 ]```
### load
Using netsim-tool load users can load existing netsim networks into new NSO running instance. Issuing this command will load devices in netsim network specified in _config->netsim-dir_.
```admin@ncs(config)# netsim load```
### update-network
When changing NSO versions, existing netsim networks might stop working. With update-network action users can change schema files (.fxs)
in the network with the ones from current NSO, which enables netsim devices to work with current version.
```netsim update-network ncs-run /home/cisco/ncs-run```






