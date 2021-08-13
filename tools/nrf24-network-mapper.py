#!/usr/bin/env python3
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

import logging

from nrf24_base import Nrf24Base


class Nrf24NetworkMapper(Nrf24Base):
    def __init__(self):
        super(Nrf24NetworkMapper, self).__init__('./nrf24-network-mapper.py')

        # Parse command line arguments and initialize the radio
        self.enable_address()
        self.enable_ack_timeout()
        self.enable_retries()
        self.enable_ping_payload()
        self.parse_and_init()

    def execute(self):
        # Put the radio in sniffer mode (ESB w/o auto ACKs)
        self.radio.enter_sniffer_mode(self.address)

        # Ping each address on each channel args.passes number of times
        valid_addresses = []
        for p in range(2):

            # Step through each potential address
            for b in range(256):

                try_address = chr(b) + self.address[1:]
                logging.info('Trying address {0}'.format(':'.join('{:02X}'.format(ord(b)) for b in try_address[::-1])))
                self.radio.enter_sniffer_mode(try_address)

                # Step through each channel
                for c in range(len(self.args.channels)):
                    self.radio.set_channel(self.channels[c])

                    # Attempt to ping the address
                    if self.radio.transmit_payload(self.ping_payload, self.ack_timeout, self.retries):
                        valid_addresses.append(try_address)
                        logging.info('Successful ping of {0} on channel {1}'.format(
                            ':'.join('{:02X}'.format(ord(b)) for b in try_address[::-1]),
                            self.channels[c]))

        # Print the results
        valid_addresses = list(set(valid_addresses))
        for addr in valid_addresses:
            logging.info('Found address {0}'.format(':'.join('{:02X}'.format(ord(b)) for b in addr[::-1])))


if __name__ == '__main__':
    Nrf24NetworkMapper().execute()
