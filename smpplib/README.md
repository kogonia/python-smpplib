python-libsmpp
==============

SMPP library for Python3 . Forked from [github](https://github.com/podshumok/python-smpplib)

Adopded for russian telecom providers and python3
Example:
```python
# coding=utf8

import datetime
import pytz

import logging
import sys

import smpplib.gsm
import smpplib.client
import smpplib.consts

# if you want to know what's happening
logging.basicConfig(level='DEBUG')

client = smpplib.client.Client('123.456.789.101', 1123)


# Print when obtain message_id
# client.set_message_sent_handler(
#    lambda pdu: sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id)))

def getPdu(pdu):
    print('Parsed pdu:', pdu.parsed)

client.set_message_received_handler(getPdu)

client.connect()
client.bind_transceiver(system_id='1234', password='5678')

parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts('Руский из питона 3, кодировочку зажги!\n')

for part in parts:
    pdu = client.send_message(

        source_addr_ton=smpplib.consts.SMPP_TON_NWSPEC,
        source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
        source_addr='1591',

        dest_addr_ton=smpplib.consts.SMPP_TON_NATNL,
        dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
        # Make sure thease two params are byte strings, not unicode:
        destination_addr='79531498486',
        short_message=part,

        data_coding=encoding_flag,
        esm_class=msg_type_flag,
        registered_delivery=True,
    )
    print(pdu.sequence)

client.listen()

```
You also may want to listen in a thread:
```python
from threading import Thread
t = Thread(target=client.listen)
t.start()
```

The client supports setting a custom generator that produces sequence numbers for the PDU packages. Per default a simple in memory generator is used which in conclusion is reset on (re)instantiation of the client, e.g. by an application restart. If you want to keep the sequence number to be persisted across restarts you can implement your own storage backed generator.

Example:
```python
import smpplib.client

import mymodule

generator = mymodule.PersistentSequenceGenerator()
client = smpplib.client.Client('example.com', SOMEPORTNUMBER, sequence_generator=generator)
...
```
