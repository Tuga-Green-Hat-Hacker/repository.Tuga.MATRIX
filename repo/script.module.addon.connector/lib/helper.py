# -*- coding: utf-8 -*-
"""
    Copyright (C) 2015 Rick Phillips @ruuk (script.module.addon.signals)
    Copyright (C) 2021 Stefano Gottardo @CastagnaIT (script.module.addon.connector)
    Helper methods

    SPDX-License-Identifier: LGPL-2.1-or-later
    See LICENSE.txt for more information.
"""
RETURN_CALL_PREFIX = '__returncall__'
SENDER_ID_SUFFIX = '.ADDONCONNECTOR'

# Types of data serialization:
SER_TYPE_PICKLE = 'pickle'
"""Pickle serialization: unlike JSON this is much faster and can serialize python objects"""
SER_TYPE_JSON = 'json'
"""Json serialization: can serialize only JSON format type"""
SER_TYPE_STRING = 'str'  # To the receiver the callback function should not have more than one mandatory arguments
"""String (utf-8): fastest method without serialization"""
SER_TYPE_NONE = 'none'  # To the receiver the callback function should not have mandatory arguments
"""Force no serialization and no data will be sent"""

JSONRPC_NOTIFYALL_STR = (
    '{{"id": 0, "jsonrpc": "2.0", "method": "JSONRPC.NotifyAll", "params": '
    '{{"message": "{callback_name}.{ser_type}.{ser_type_return}",'
    ' "sender": "{sender_id}{sender_id_suffix}", "data": "{data}"}}'
    '}}')


class AddonConnectorException(Exception):
    """Common base class for all AddonConnectorException exceptions"""


class WaitTimeoutError(AddonConnectorException):
    """Exception used when waiting times out"""


class OperationAbortedError(AddonConnectorException):
    """Kodi has requested to abort the operation"""


def get_addon_id():
    """Return the Kodi add-on ID of the add-on that has loaded the module"""
    if not hasattr(get_addon_id, 'cached'):
        from xbmcaddon import Addon
        get_addon_id.cached = Addon().getAddonInfo('id')
    return get_addon_id.cached


def deserialize_data(ser_type, data):
    """Deserialize the data according to the specified serialisation type"""
    from base64 import b64decode
    if ser_type == SER_TYPE_PICKLE:
        from pickle import loads
        data = b64decode(data)
        return loads(data)
    if ser_type == SER_TYPE_JSON:
        from json import loads
        from sys import version_info
        _data = b64decode(data)
        # NOTE: With Python 3.5 and older json.loads() does not support bytes or bytearray
        return loads(_data if version_info > (3, 5) else _data.decode('utf-8'))
    if ser_type == SER_TYPE_STRING:
        return b64decode(data).decode('utf-8')
    if ser_type == SER_TYPE_NONE:
        return None
    raise AddonConnectorException('The specified type of serialization "{}" is not supported'.format(ser_type))


def serialize_data(ser_type, data):
    """Serialize the data according to the specified serialisation type"""
    # NOTE: The return data must be always an ASCII string because we perform the Kodi JSON-RPC call
    #       with a string (see _make_signal_call) this allow us to avoid to the slow JSON encoding, then we are
    #       forced to serialise the data with b64encode to have an ASCII string but is much faster than JSON
    from base64 import b64encode
    if ser_type == SER_TYPE_PICKLE:
        from pickle import dumps, HIGHEST_PROTOCOL
        _data = dumps(data, HIGHEST_PROTOCOL)
        return b64encode(_data).decode('ascii')
    if ser_type == SER_TYPE_JSON:
        # Here you could think to return the json.dumps directly,
        # but Kodi performs others internal JSON conversions and this makes performance much worse
        from json import dumps
        _data = dumps(data).encode('utf-8')
        return b64encode(_data).decode('ascii')
    if ser_type == SER_TYPE_STRING:
        if isinstance(data, tuple):
            if data[1]:
                raise AddonConnectorException('With SER_TYPE_STRING kwargs are not supported')
            args_count = len(data[0])
            if args_count > 1:
                raise AddonConnectorException('With SER_TYPE_STRING only until to one argument is supported')
            if args_count == 1:
                _data = data[0][0]
            else:
                _data = ''
        else:
            _data = data
        if not isinstance(_data, str):
            raise AddonConnectorException('The data are not of string type')
        return b64encode(_data.encode('utf-8')).decode('ascii')
    if ser_type == SER_TYPE_NONE:
        return ''
    raise AddonConnectorException('The specified type of serialization "{}" is not supported'.format(ser_type))


class CallConfig:
    """Call configuration"""
    def __init__(self, callback_name, addon_id=None, timeout_secs=10,
                 ser_type=SER_TYPE_PICKLE, ser_type_return=None):
        """
        :param callback_name: the name bound to the function to call (usually the function name)
        :param addon_id: the ID of the add-on that will receive this call (specify only to call others add-ons)
        :param timeout_secs: maximum waiting time before raise timeout (not used on 'make_signal_call')
        :param ser_type: type of data serialization to be used to send the data
        :param ser_type_return: type of data serialization to be used to receive the data, if different from sending
        """
        self.callback_name = callback_name
        self.addon_id = addon_id or get_addon_id()
        self.timeout_secs = timeout_secs
        self.ser_type = ser_type
        self.ser_type_return = ser_type_return or ser_type

    def change_name(self, callback_name):
        """Change the name bound to the function to be called and return the updated class object"""
        self.callback_name = callback_name
        return self
