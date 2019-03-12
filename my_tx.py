#! /usr/bin/python3
# coding=utf8

import pytz
import datetime
from time import sleep

import logging
import sys

import smpplib.gsm
import smpplib.client
import smpplib.consts
import settings


logging.basicConfig(
    filename='/var/log/sms/msg.log',
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.INFO)

if (len(sys.argv)>1):
    PHONES=str(sys.argv[1])
    MSG=' '.join(sys.argv[2:])
client = None

try:
    client = smpplib.client.Client(settings.sms_host, settings.sms_port)
    client.set_message_sent_handler(
        lambda pdu: sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id)))

    client.connect()
    try:
        client.bind_transmitter(system_id=settings.sms_id, password=settings.sms_pass)

        parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(MSG)
        logging.info('Text: %s', MSG)
        for part in parts:
            LIST_PHONES=PHONES.split("\\n")
            for PHONE in LIST_PHONES:
                DST_ADDR = PHONE.strip()
                if len(DST_ADDR) == 11:
                    pdu = client.send_message(
                        source_addr_ton=smpplib.consts.SMPP_TON_ALNUM,
                        source_addr_npi=smpplib.consts.SMPP_NPI_UNK,
                        source_addr="SMPP",

                        dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
                        dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
                        destination_addr=DST_ADDR,
                        short_message=part,

                        data_coding=encoding_flag,
                        esm_class=msg_type_flag,
                        registered_delivery=True,
                    )
                    
            logging.info('Send to %s', LIST_PHONES)
            logging.info('=====================')
            sleep(0.05)
    finally:
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
        client.disconnect()
