# Addon connector for Kodi (script.module.addon.connector)

[![Kodi version](https://img.shields.io/badge/kodi%20versions-19-blue)](https://kodi.tv/)
[![GitHub release](https://img.shields.io/github/release/CastagnaIT/script.module.addon.connector.svg)](https://github.com/CastagnaIT/script.module.addon.connector/releases)
[![CI](https://github.com/CastagnaIT/script.module.addon.connector/workflows/CI/badge.svg)](https://github.com/CastagnaIT/script.module.addon.connector/actions?query=workflow:CI)
[![Codecov](https://img.shields.io/codecov/c/github/CastagnaIT/script.module.addon.connector/master)](https://codecov.io/gh/CastagnaIT/script.module.addon.connector/branch/master)
[![License: LGPL-2.1 or later](https://img.shields.io/badge/license-LGPLv2.1_or_later-blue)](https://opensource.org/licenses/LGPL-2.1)
[![Contributors](https://img.shields.io/github/contributors/CastagnaIT/script.module.addon.connector.svg)](https://github.com/CastagnaIT/script.module.addon.connector/graphs/contributors)

A Kodi module to provide communication between add-ons and add-ons services.

***Project temporary stopped due to a memory leak on Kodi JSON-RPC call:***
https://github.com/xbmc/xbmc/issues/19332


## Main features

- Allows exchanging data between an add-on to his service or another add-on service
- Allows exchanging data between an add-on to another add-on
- Allows exchanging data between multiple add-on services
- Allows call a function of another add-on or service (no return data)
- With the default data serialization ([pickle](https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled))
you can transfer the most python data types
- Supports automatic forwarding of the exceptions to the add-on that made the call

## How integrate it into your add-on

A quick example of add-on communication, to allow data to be sent and received between the add-on and its service.

We assume that you have already developed a Kodi add-on with [his service](https://kodi.wiki/view/Service_add-ons),
then in the add-on script, we make the call to his service in order to send and ask some data: 

```python
import addonconnector
import xbmc

CALL_CFG = addonconnector.CallConfig(None)

def ask_data_to_service():
    ret_data = addonconnector.make_call(CALL_CFG.signal_name('the_service_function'),
                                        'sun', color='yellow')
    xbmc.log('Response received from the service: ' + ret_data)
```

On the service script of the add-on, we handle the callback, to answer to the add-on call request:

```python
import addonconnector
import xbmc

def the_service_function(name, color='blue'):
    xbmc.log('The add-on has asked if the {} is {}.'.format(name, color))
    data = 'Yes it is!' if color == 'yellow' else 'Nope!'
    # Here you can return any kind of data also the raised exceptions will be forwarded
    return data

if __name__ == '__main__':
    monitor = xbmc.Monitor()
    addonconnector.register_callback(the_service_function)
    while not monitor.abortRequested():
    # ...follow the Kodi add-on service development example
```

You can find all the detailed instructions and others examples are on the Wiki pages.

## Download links

Install add-on via repository - provide automatic installation of updates:

Todo

## License

Licensed under GNU Lesser General Public License version 2.1.

## Credits

This module is based on the "Addon Signals" module, thanks to Rick Phillips (Ruuk) who developed Addon Signals module:<br/>
https://github.com/ruuk/script.module.addon.signals
