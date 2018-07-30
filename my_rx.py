#!/usr/bin/python3

import re
import smpplib
import settings
import sys

client = None

try:
    client = smpplib.client.Client(settings.sms_host, settings.sms_port)
    client.connect()
    try:
        client.bind_receiver(system_id=settings.sms_id, password=settings.sms_pass)
        data=client.listen()

    finally:
        print ("==client.state====", client.state)
        if client.state in [smpplib.consts.SMPP_CLIENT_STATE_BOUND_TX]:
            try:
                client.unbind()
            except smpplib.exceptions.UnknownCommandError as ex:
                try:
                    client.unbind()
                except smpplib.exceptions.PDUError as ex:
                    pass
finally:
    if client:
        print ("==client.state====", client.state)
        client.disconnect()
        print ("==client.state====", client.state)
