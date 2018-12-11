#!/usr/bin/python3

import re
import smpplib
import settings
import sys
import logging

logging.basicConfig(
    filename='/var/log/sms/msg.log',
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.INFO)

MSG=None

if (len(sys.argv)>1):
    PHONES=str(sys.argv[1])
    MSG=' '.join(sys.argv[2:])
client = None

try:
    client = smpplib.client.Client(settings.sms_host, settings.sms_port)
    client.connect()
    print(client.state) 
    try:
        client.bind_transmitter(system_id=settings.sms_id, password=settings.sms_pass)
        for PHONE in PHONES.split("\r\n"):
            DST_ADDR = PHONE.strip()
            print("Phone number = ", DST_ADDR, " length = ",len(DST_ADDR),"<br />")
            if MSG:
                logging.info('Text: %s', MSG)
                if len(DST_ADDR) == 11:
                    logging.info('Send to %s', DST_ADDR)
                    client.send_message(source_addr='SMPP',
                        source_addr_ton=5,
                        source_addr_npi=0,
                        dest_addr_ton=1,
                        dest_addr_npi=1,
                        destination_addr=DST_ADDR,
                        short_message=MSG.encode('cp1251'))
    finally:
#        print ("==client.state====", client.state)
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
#        print ("==client.state====", client.state)
        client.disconnect()
#        print ("==client.state====", client.state)

