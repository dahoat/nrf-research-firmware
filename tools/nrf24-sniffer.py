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
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import time

from nrf24_base import Nrf24Base


class Nrf24Sniffer(Nrf24Base):

    def __init__(self):
        super(Nrf24Sniffer, self).__init__('./nrf24-sniffer.py')

        # Parse command line arguments and initialize the radio
        self.enable_address()
        self.enable_timeout()
        self.enable_ack_timeout()
        self.enable_retries()
        self.enable_ping_payload()

        self.parse_and_init()

    def execute(self):
        # Put the radio in sniffer mode (ESB w/o auto ACKs)
        self.radio.enter_sniffer_mode(self.address)

        # Sweep through the channels and decode ESB packets in pseudo-promiscuous mode
        last_ping = time.time()
        channel_index = 0
        while True:

            # Follow the target device if it changes channels
            if time.time() - last_ping > self.timeout:

                # First try pinging on the active channel
                if not self.radio.transmit_payload(self.ping_payload, self.ack_timeout, self.retries):

                    # Ping failed on the active channel, so sweep through all available channels
                    success = False
                    for channel_index in range(len(self.channels)):
                        self.radio.set_channel(self.channels[channel_index])
                        if self.radio.transmit_payload(self.ping_payload, self.ack_timeout, self.retries):
                            # Ping successful, exit out of the ping sweep
                            last_ping = time.time()
                            logging.debug('Ping success on channel {0}'.format(self.channels[channel_index]))
                            success = True
                            break

                    # Ping sweep failed
                    if not success:
                        logging.debug('Unable to ping {0}'.format(self.address_string))

                # Ping succeeded on the active channel
                else:
                    logging.debug('Ping success on channel {0}'.format(self.channels[channel_index]))
                    last_ping = time.time()

            # Receive payloads
            value = self.radio.receive_payload()
            if value[0] == 0:
                # Reset the channel timer
                last_ping = time.time()

                # Split the payload from the status byte
                payload = value[1:]

                # Log the packet
                logging.info('{0: >2}  {1: >2}  {2}  {3}'.format(
                    self.channels[channel_index],
                    len(payload),
                    self.address_string,
                    ':'.join('{:02X}'.format(b) for b in payload)))


if __name__ == "__main__":
    Nrf24Sniffer().execute()
