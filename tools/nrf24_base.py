"""
  Copyright (C) 2016 Bastille Networks

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse

from nrf24 import *


def _init_args_parser(description) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description,
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=50,
                                                                                         width=120))
    parser.add_argument('-c', '--channels', type=int, nargs='+', help='RF channels', default=range(2, 84),
                        metavar='N')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output', default=False)
    parser.add_argument('-l', '--lna', action='store_true', help='Enable the LNA (for CrazyRadio PA dongles)',
                        default=False)
    parser.add_argument('-i', '--index', type=int, help='Dongle index', default=0)
    return parser


def _args_hex_to_bytes(arg: str) -> bytes:
    return bytes.fromhex(arg.replace(':', ''))


class Nrf24Base:
    channels = []
    args = None
    parser = None
    radio = None

    address_enabled = False
    _address = None

    optional_attributes = {
        'address': {
            'enabled': False,
            'value': None,
            'setter': 'set_address'
        },
        'address_string': {
            'enabled': False,
            'value': None,
            'setter': None
        },
        'timeout': {
            'enabled': False,
            'value': None,
            'setter': 'set_timeout'
        },
        'ack_timeout': {
            'enabled': False,
            'value': None,
            'setter': 'set_ack_timeout'
        },
        'retries': {
            'enabled': False,
            'value': None,
            'setter': 'set_retries'
        },
        'ping_payload': {
            'enabled': False,
            'value': None,
            'setter': 'set_ping_payload'
        },
        'prefix_address': {
            'enabled': False,
            'value': None,
            'setter': 'set_prefix_address'
        },
        'dwell_time': {
            'enabled': False,
            'value': None,
            'setter': 'set_dwell_time'
        },
    }

    def __init__(self, description):
        # Initialize the argument parser
        self.parser = _init_args_parser(description)

    def __getattribute__(self, item):
        optional_attributes = super(Nrf24Base, self).__getattribute__('optional_attributes')
        if item in optional_attributes:
            entry = optional_attributes[item]
            if not entry['enabled']:
                raise ValueError("This property needs to be activated in the constructor: " + item)
            else:
                return entry['value']
        else:
            return super(Nrf24Base, self).__getattribute__(item)

    def __setattr__(self, key, value):
        if key in self.optional_attributes:
            raise ValueError(
                "This property needs to be activated in the constructor and cannot be accessed directly: " + key)
        else:
            super(Nrf24Base, self).__setattr__(key, value)

    def enable_address(self):
        self.parser.add_argument('-a', '--address', type=str, help='Address to sniff, following as it changes channels',
                                 required=True)
        self._enable_optional_property('address')
        self._enable_optional_property('address_string')

    def set_address(self):
        address = _args_hex_to_bytes(self.args.address)[::-1][:5]
        address_string = ':'.join('{:02X}'.format(b) for b in address[::-1])
        if len(address) < 2:
            raise Exception('Invalid address: {0}'.format(self.args.address))
        self._set_optional_property('address', address)
        self._set_optional_property('address_string', address_string)

    def enable_timeout(self):
        self.parser.add_argument('-t', '--timeout', type=float, help='Channel timeout, in milliseconds', default=100)
        self._enable_optional_property('timeout')

    def set_timeout(self):
        # Convert channel timeout from milliseconds to seconds
        timeout = float(self.args.timeout) / float(1000)
        self._set_optional_property('timeout', timeout)

    def enable_ack_timeout(self):
        self.parser.add_argument('-k', '--ack_timeout', type=int,
                                 help='ACK timeout in microseconds, accepts [250,4000], step 250', default=250)
        self._enable_optional_property('ack_timeout')

    def set_ack_timeout(self):
        # Format the ACK timeout value
        ack_timeout = int(self.args.ack_timeout / 250) - 1
        ack_timeout = max(0, min(ack_timeout, 15))
        self._set_optional_property('ack_timeout', ack_timeout)

    def enable_retries(self):
        self.parser.add_argument('-r', '--retries', type=int, help='Auto retry limit, accepts [0,15]', default=1,
                                 choices=range(0, 16), metavar='RETRIES')
        self._enable_optional_property('retries')

    def set_retries(self):
        # Format the retry value
        retries = max(0, min(self.args.retries, 15))
        self._set_optional_property('retries', retries)

    def enable_ping_payload(self):
        self.parser.add_argument('-p', '--ping_payload', type=str, help='Ping payload, ex 0F:0F:0F:0F',
                                 default='0F:0F:0F:0F', metavar='PING_PAYLOAD')
        self._enable_optional_property('ping_payload')

    def set_ping_payload(self):
        # Parse the ping payload
        ping_payload = _args_hex_to_bytes(self.args.ping_payload)
        self._set_optional_property('ping_payload', ping_payload)

    def enable_prefix_address(self):
        self.parser.add_argument('-p', '--prefix', type=str, help='Promiscuous mode address prefix', default='')
        self._enable_optional_property('prefix_address')

    def set_prefix_address(self):
        # Parse the prefix addresses
        prefix_address = _args_hex_to_bytes(self.args.prefix)
        if len(prefix_address) > 5:
            raise Exception('Invalid prefix address: {0}'.format(self.args.address))
        self._set_optional_property('prefix_address', prefix_address)

    def enable_dwell_time(self):
        self.parser.add_argument('-d', '--dwell', type=float, help='Dwell time per channel, in milliseconds',
                                 default='100')
        self._enable_optional_property('dwell_time')

    def set_dwell_time(self):
        # Convert dwell time from milliseconds to seconds
        dwell_time = self.args.dwell / 1000
        self._set_optional_property('dwell_time', dwell_time)

    def _enable_optional_property(self, item):
        self.optional_attributes[item]['enabled'] = True

    def _set_optional_property(self, key, value):
        self.optional_attributes[key]['value'] = value

    # Parse and process common command line arguments
    def parse_and_init(self):
        # Parse the command line arguments
        self.args = self.parser.parse_args()

        # Setup logging
        level = logging.DEBUG if self.args.verbose else logging.INFO
        logging.basicConfig(level=level, format='[%(asctime)s.%(msecs)03d]  %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

        # Set the channels
        channels = self.args.channels
        logging.debug('Using channels {0}'.format(', '.join(str(c) for c in channels)))

        # Initialize the radio
        self.radio = Nrf24(self.args.index)
        if self.args.lna:
            self.radio.enable_lna()

        # Set values of optional properties
        for item, entry in self.optional_attributes.items():
            if entry['enabled'] and entry['setter'] is not None:
                setter = getattr(self, entry['setter'])
                setter()
