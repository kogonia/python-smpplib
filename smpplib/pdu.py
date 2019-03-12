#
# smpplib -- SMPP Library for Python
# Copyright (c) 2005 Martynas Jocius <mjoc@akl.lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# Modified by Yusuf Kaka <yusufk at gmail>
# Added support for Optional TLV's
# Modified by Kirill Kirsanov <kkrisanov@gmail.com>
# Added PDU parser

"""PDU module"""

import struct

from . import command_codes
from . import consts

SMPP_ESME_ROK = 0x00000000


def extract_command(pdu):
    """Extract command from a PDU"""

    code = struct.unpack('>L', pdu[4:8])[0]
    return command_codes.get_command_name(code)


class default_client(object):
    """Dummy client"""
    sequence = 0


import binascii


def chunks(li, n):
    if not li:
        return
    yield li[:n]
    yield from chunks(li[n:], n)


class PDUParser():
    def _readX(self, field, ln):
        if len(self._raw) >= self._pos + ln:
            pos = self._pos
            self._pdu[field] = self._raw[pos:pos + ln]
            import binascii

            self._pos = pos + ln

    def _read2(self, field):
        if len(self._raw) >= self._pos + 2:
            pos = self._pos
            self._pdu[field] = int(self._raw[pos:pos + 2], 16)
            self._pos = pos + 2

    def _read4(self, field):
        if len(self._raw) >= self._pos + 4:
            pos = self._pos
            self._pdu[field] = int(self._raw[pos:pos + 4], 16)
            self._pos = pos + 4

    def _readField(self, field):
        pos = self._pos
        self._pdu[field] = self._readString()
        self._pos = pos + len(self._pdu[field]) * 2 + 2

    def _readString(self):
        st = ''
        for chunk in chunks(self._raw[self._pos:], 2):
            if chunk == b'00':
                return st
            else:
                st += chr(int(chunk, 16))

    def _readHeader(self):
        for i, chunk in enumerate(chunks(self._raw, 8)):
            if i == 0:
                self._pdu['cmdlen'] = int(chunk, 16)
                continue
            if i == 1:
                self._pdu['cmdid'] = chunk

            if i == 2:
                self._pdu['stat'] = int(chunk, 16)
                continue
            if i == 3:
                self._pdu['seq'] = int(chunk, 16)
                continue
            self._pos = 8 * 4
            break

    def _parseCMD(self, st):
        """
        прарсер "[(type name)]"-> eval
        type = s строка | 2 Int | ls Строка с длинной
        name = String
        """

        state = 'read type'  # state =  read type | read s | read 2 | read ls

        while len(st) != len(st.replace("  ", " ")):
            st = st.replace("  ", " ")
        for token in st.split(" "):
            if self._pos>=len(self._raw):
                #print('overflow', self._pos)
                break
            if state == "read type":
                if token == 's':
                    state = 'read s'
                    continue
                if token == '2':
                    state = 'read 2'
                    continue
                if token == '4':
                    state = 'read 4'
                    continue
                if token == 'ls':
                    state = 'read ls'
                    continue
                if token == 'pl':
                    state = 'read payload'
                    continue

            if state == 'read s':
                self._readField(token)
                state = 'read type'
                continue
            if state == 'read 2':
                self._read2(token)
                state = 'read type'
                continue
            if state == 'read 4':
                self._read4(token)
                state = 'read type'
                continue
            if state == 'read ls':
                self._readX(token, self._pdu['smlen'] * 2)
                if self._pdu['dcs'] == 8:
                    self._pdu[token] = binascii.unhexlify(self._pdu[token]).decode('utf-16-be')
                if self._pdu['dcs'] in [0, 1, 2, 3]:
                    self._pdu[token] = binascii.unhexlify(self._pdu[token]).decode('latin1')
                state = 'read type'
                continue
            if state == 'read payload':
                self._readX(token, self._pdu['paylen'] * 2)
                if self._pdu['dcs'] == 8:
                    self._pdu[token] = binascii.unhexlify(self._pdu[token]).decode('utf-16-be')
                if self._pdu['dcs'] in [0, 1, 2, 3]:
                    self._pdu[token] = binascii.unhexlify(self._pdu[token]).decode('latin1')
                state = 'read type'
                continue

    def __init__(self, pdu, mode='ascii'):
        """
        :param pdu:
        :param mode: ascii/bin
        """
        if mode == 'bin':
            import binascii
            self._raw = binascii.b2a_hex(pdu)
        else:
            self._raw = pdu
        self._pos = 0
        self._pdu = {}
        self._readHeader()

    def parse(self):
        # парсинг _raw
        # типы данных - s, 2, ls
        # распарсеные значения складаываются в _pdu
        if self._pdu['cmdid'] in [b'80000001', b'80000001', b'80000009']:
            self._parseCMD('s sysid')
        if self._pdu['cmdid'] in [b'00000001', b'00000002', b'00000009']:
            self._parseCMD('s sysid s passwd s systype s intver 2 addrton 2 addrnpi s ddrrange')
        if self._pdu['cmdid'] in [b'80000004', b'80000005', b'80000103']:
            self._parseCMD('s msgid')
        if self._pdu['cmdid'] in [b'00000004', b'00000005']:
            self._parseCMD("s servtype 2 saddrton 2 saddrnpi s saddress 2 daddrton 2 daddrnpi s daddress " +
                           "2 esm 2 pid 2 priority s sdt s valt 2 rdel 2 rip 2 dcs 2 smid 2 smlen ls sm " +
                           "4 tag 4 paylen pl payload")
        if self._pdu['cmdid'] in [b'00000103']:
            self._parseCMD('s servtype 2 saddrton 2 saddrnpi s saddress 2 daddrton 2 daddrnpi s daddress ' +
                           "2 esm 2 rdel 2 dcs")
        if self._pdu['cmdid'] in [b'00000003']:
            self._parseCMD("s servtype 2 saddrton 2 saddrnpi s saddress")
        if self._pdu['cmdid'] in [b'80000003']:
            self._parseCMD("s servtype s findate 2 msgtdate 2 error")
        if self._pdu['cmdid'] in [b'00000008']:
            self._parseCMD("s servtype s msgid 2 saddrton 2 saddrnpi s saddress 2 daddrton 2 daddrnpi s daddress ")
        if self._pdu['cmdid'] in [b'00000007']:
            self._parseCMD("s msgid 2 saddrton 2 saddrnpi s saddress s sdt s valt 2 rdel 2 rip 2 smlen ls sm")
        if self._pdu['cmdid'] in [b'00000102']:
            self._parseCMD("2 saddrton 2 saddrnpi s saddress 2 eaddrton 2 eaddrnpi s eaddress")
        self._pos = 32
        return self._pdu


class PDU(object):
    """PDU class"""

    length = 0
    command = None
    status = None
    _sequence = None

    def __init__(self, client=default_client(), **kwargs):
        """Singleton dummy client will be used if omitted"""
        if client is None:
            self._client = default_client()
        else:
            self._client = client

    def _get_sequence(self):
        """Return global sequence number"""
        return self._sequence if self._sequence is not None else \
            self._client.sequence

    def _set_sequence(self, sequence):
        """Setter for sequence"""
        self._sequence = sequence

    sequence = property(_get_sequence, _set_sequence)

    def _next_seq(self):
        """Return next sequence number"""
        return self._client.next_sequence()

    def is_vendor(self):
        """Return True if this is a vendor PDU, False otherwise"""
        return hasattr(self, 'vendor')

    def is_request(self):
        """Return True if this is a request PDU, False otherwise"""
        return not self.is_response()

    def is_response(self):
        """Return True if this is a response PDU, False otherwise"""
        if command_codes.get_command_code(self.command) & 0x80000000:
            return True
        return False

    def is_error(self):
        """Return True if this is an error response, False otherwise"""
        if self.status != SMPP_ESME_ROK:
            return True
        return False

    def get_status_desc(self, status=None):
        """Return status description"""

        if status is None:
            status = self.status

        try:
            desc = consts.DESCRIPTIONS[status]
        except KeyError:
            return "Description for status 0x%x not found!" % status

        return desc

    def parse(self, data):

        """Parse raw PDU"""

        header = data[0:16]
        chunks = struct.unpack('>LLLL', header)
        self.length = chunks[0]
        self.command = extract_command(data)
        self.status = chunks[2]
        self.sequence = chunks[3]

        if len(data) > 30:
            try:
                pdp = PDUParser(data, 'bin')
                self.parsed = pdp.parse()
                return self.parsed
            except Exception as e:
                print(e)

    def _unpack(self, fmt, data):
        """Unpack values. Uses struct.unpack. TODO: remove this"""
        return struct.unpack(fmt, data)

    def generate(self):
        """Generate raw PDU"""

        body = self.generate_params()

        self._length = len(body) + 16

        command_code = command_codes.get_command_code(self.command)

        header = struct.pack(">LLLL", self._length, command_code,
                             self.status, self.sequence)

        return header + body

