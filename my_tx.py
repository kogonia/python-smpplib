#!/usr/bin/python3

import re
import smpplib
import settings
import sys

MSG=None
if (len(sys.argv)>1):
    DST_ADDR=sys.argv[1]
    MSG=' '.join(sys.argv[2:])

client = None
try:
    client = smpplib.client.Client(settings.sms_host, settings.sms_port)
    client.connect()
    try:
        client.bind_transmitter(system_id=settings.sms_id, password=settings.sms_pass)

        if MSG:
            client.send_message(source_addr='wanted_number_to_display',
                source_addr_ton=0,
                source_addr_npi=1,
                dest_addr_ton=1,
                dest_addr_npi=1,
                destination_addr=DST_ADDR,
                short_message=MSG.encode('cp1251'))

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
