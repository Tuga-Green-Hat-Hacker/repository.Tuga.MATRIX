# -*- coding: utf-8 -*-
"""
    Copyright (C) 2015 Rick Phillips @ruuk (script.module.addon.signals)
    Copyright (C) 2021 Stefano Gottardo @CastagnaIT (script.module.addon.connector)
    Mechanism for Kodi to provide communication between add-ons and add-ons services

    SPDX-License-Identifier: LGPL-2.1-or-later
    See LICENSE.txt for more information.
"""
__all__ = ['AddonConnectorException', 'CallConfig', 'deserialize_data', 'get_addon_id', 'JSONRPC_NOTIFYALL_STR',
           'OperationAbortedError', 'RETURN_CALL_PREFIX', 'SER_TYPE_JSON', 'SER_TYPE_NONE', 'SER_TYPE_PICKLE',
           'SER_TYPE_STRING', 'serialize_data', 'WaitTimeoutError']

from typing import Tuple

from xbmc import executeJSONRPC, Monitor, sleep, log, LOGERROR

from helper import (SER_TYPE_PICKLE, SER_TYPE_JSON, SER_TYPE_STRING, JSONRPC_NOTIFYALL_STR, serialize_data,
                    deserialize_data, CallConfig, RETURN_CALL_PREFIX, AddonConnectorException, WaitTimeoutError,
                    OperationAbortedError, get_addon_id, SER_TYPE_NONE, SENDER_ID_SUFFIX)


def use_multithread(value=False):
    """
    If set as True allow to receive multiple callbacks at same time, by creating a thread for each call.
    Must be set only one time, before registering the callbacks
    """
    _receiver().use_multithread = value


def _receiver():
    """Return the CallReceiver instance"""
    if not hasattr(_receiver, 'cached'):
        _receiver.cached = CallReceiver()
    return _receiver.cached


class CallReceiver(Monitor):
    """Monitor to receive the RPC calls"""
    def __init__(self):
        self.slots = {}
        self.use_multithread = False
        super().__init__()

    def register_slot(self, callback_name, callback, addon_id=None, ser_type_return=None, use_thread=None):
        """Register a slot"""
        if addon_id not in self.slots:
            self.slots[addon_id] = {}
        # Add the slot properties
        self.slots[addon_id][callback_name] = {
            'callback_func': callback,
            'ser_type_return': ser_type_return,
            'run_threaded': self.use_multithread if use_thread is None else use_thread
        }

    def unregister_slot(self, callback_name, addon_id):
        """Unregister a slot"""
        if addon_id not in self.slots:
            return
        if callback_name not in self.slots[addon_id]:
            return
        del self.slots[addon_id][callback_name]

    def unregister_slots(self, addon_id=None):
        """Unregister all slots or all slots of the specified add-on ID"""
        if addon_id is None:
            self.slots = {}
        elif addon_id in self.slots:
            del self.slots[addon_id]

    def onNotification(self, sender, method, data):  # pylint: disable=invalid-name
        """The Kodi Monitor event handler for notifications"""
        try:
            if not sender.endswith(SENDER_ID_SUFFIX):
                return
            # Get the addon id
            addon_id, _ = sender.rsplit('.', 1)
            if addon_id not in self.slots:
                return
            # Get the callback name and type of data serializations
            # 'method' have a value like: 'Other.theCallbackName.sertype.sertype_return'
            _, callback_name, ser_type, ser_type_return = method.split('.')
            if callback_name not in self.slots[addon_id]:
                return
            # Save the serialization type for a possible automatic RPC return call
            self.slots[addon_id][callback_name]['ser_type_return'] = ser_type_return
            # Get the add-on function, bound to the callback_name
            func = self.slots[addon_id][callback_name]['callback_func']
        except Exception as exc:  # pylint: disable=broad-except
            from traceback import format_exc
            log(format_exc(), LOGERROR)
            raise AddonConnectorException('Internal error see log details') from exc
        # Deserialize the data according to the specified serialisation type
        if callback_name.startswith(RETURN_CALL_PREFIX) or ser_type in [SER_TYPE_STRING, SER_TYPE_NONE]:
            args = (deserialize_data(ser_type, data),)
            kwargs = {}
        else:
            args, kwargs = deserialize_data(ser_type, data)
        # Execute the function
        if self.slots[addon_id][callback_name]['run_threaded']:
            from threading import Thread
            Thread(target=func, args=args, kwargs=kwargs).start()
        else:
            # NOTE: Executing the function is a blocking call (it is executed on the same thread of the add-on),
            # then all the subsequents notifications will be queued to the current one, this means that the function of
            # the next RPC call will be executed only when the current called function has finished its execution
            func(*args, **kwargs)


class CallHandler:
    """Handle a RPC call and wait the RPC return call"""
    def __init__(self, call_config: 'CallConfig', args, kwargs):
        self._call_config = call_config
        self._callback_data = None
        self._is_callback_received = False
        # Temporary register the slot for waiting the RPC return call from an add-on
        _receiver().register_slot(RETURN_CALL_PREFIX + call_config.callback_name,
                                  self.return_callback,
                                  call_config.addon_id,
                                  call_config.ser_type_return,
                                  False)
        # Execute the RPC call to an add-on
        _make_signal_call(call_config.callback_name, (args, kwargs), call_config.addon_id,
                          call_config.ser_type, call_config.ser_type_return)

    def return_callback(self, data):
        """Callback done by make_return_call (manually or in automatic way)"""
        self._callback_data = data
        self._is_callback_received = True

    def wait_rpc_return_call(self):
        """Wait that RPC return call send the data"""
        from time import perf_counter
        end_time = perf_counter() + self._call_config.timeout_secs
        while not self._is_callback_received:
            if perf_counter() > end_time:
                _receiver().unregister_slot(self._call_config.callback_name, self._call_config.addon_id)
                raise WaitTimeoutError
            if _receiver().abortRequested():
                raise OperationAbortedError
            sleep(10)
        _receiver().unregister_slot(self._call_config.callback_name, self._call_config.addon_id)
        if isinstance(self._callback_data, Exception):
            raise self._callback_data
        return self._callback_data


def register_callbacks(list_callbacks_args: Tuple[str, ...]):
    """
    Register more slots for functions of callbacks
    :param list_callbacks_args: List of tuples, every tuple must have the arguments to be set to 'register_callback'
    """
    for args in list_callbacks_args:
        register_callback(*args)


def register_callback(callback, callback_name=None, addon_id=None, handle_return_call=True):
    """
    Register a slot for a function of callback
    :param callback: the function to be called
    :param callback_name: custom name of the callback (if not specified will be used the function name)
    :param addon_id: the addon ID that receive the callbacks (specify only for custom actions)
    :param handle_return_call: if True will send automatically the callback to the caller add-on
                               (so forward return data and exceptions)
    """
    _callback_name = callback_name or callback.__name__
    _addon_id = addon_id or get_addon_id()
    _receiver().register_slot(_callback_name,
                              EnvelopeFuncCallback(callback,
                                                   _callback_name,
                                                   _addon_id).call_func
                              if handle_return_call else callback,
                              _addon_id)


def unregister_callback(callback_name, addon_id=None):
    """Unregister a callback"""
    _receiver().unregister_slot(callback_name, addon_id or get_addon_id())


def unregister_callbacks(addon_id=None):
    """Unregister all the callbacks bound to an add-on ID"""
    _receiver().unregister_slots(addon_id or get_addon_id())


def make_signal_call(__call_config__: 'CallConfig', *args, **kwargs):
    """
    Make a call to an add-on or service without wait to get any return data
    :param __call_config__: The call configuration
    """
    _make_signal_call(__call_config__.callback_name,
                      (args, kwargs),
                      __call_config__.addon_id,
                      __call_config__.ser_type,
                      __call_config__.ser_type_return)


def _make_signal_call(callback_name, data=None, addon_id=None, ser_type=SER_TYPE_PICKLE, ser_type_return=SER_TYPE_NONE):
    try:
        # We avoid the slow JSON encoding then we directly build the JSON data in a string
        executeJSONRPC(JSONRPC_NOTIFYALL_STR.format(
            callback_name=callback_name,
            ser_type=ser_type,
            ser_type_return=ser_type_return,
            sender_id=addon_id or get_addon_id(),
            sender_id_suffix=SENDER_ID_SUFFIX,
            data=serialize_data(ser_type, data)
        ))
    except Exception as exc:  # pylint: disable=broad-except
        from traceback import format_exc
        log(format_exc(), LOGERROR)
        raise AddonConnectorException('Internal error see log details') from exc


def make_call(__call_config__: 'CallConfig', *args, **kwargs):
    """
    Make a call to an add-on or service
    :param __call_config__: The call configuration
    :raise WaitTimeoutError: if the waiting time exceed the timeout value
    :raise OperationAbortedError: if Kodi abort the operation (e.g. Kodi exit)
    """
    return CallHandler(__call_config__, args, kwargs).wait_rpc_return_call()


def make_return_call(callback_name, data=None, addon_id=None, ser_type=SER_TYPE_PICKLE):
    """
    Make a return call to the caller add-on (that has executed the 'make_call')
    :param callback_name: the name of the function to call
    :param data: the data to return to the caller
    :param addon_id: the ID of the add-on which has executed the 'make_call' call (specify only for custom actions)
    :param ser_type: type of data serialization to be used
    """
    _make_signal_call(RETURN_CALL_PREFIX + callback_name, data, addon_id, ser_type)


class EnvelopeFuncCallback:
    """Envelope a function in order to handle a return call and catching, conversion, forwarding of exceptions"""
    def __init__(self, func, callback_name, addon_id):
        self._func = func
        self._callback_name = callback_name
        self._addon_id = addon_id

    def call_func(self, *args, **kwargs):
        """Forwards the call to the enveloped function"""
        try:
            ret_data = self._func(*args, **kwargs)
            _ser_type_return = _receiver().slots[self._addon_id][self._callback_name]['ser_type_return']
        except Exception as exc:  # pylint: disable=broad-except
            ret_data = serialize_data(SER_TYPE_PICKLE, exc)
            _ser_type_return = SER_TYPE_PICKLE
        return _make_signal_call(RETURN_CALL_PREFIX + self._callback_name,
                                 ret_data,
                                 self._addon_id,
                                 _ser_type_return)
