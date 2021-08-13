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
import time

from nrf24_base import Nrf24Base


class Nrf24Scanner(Nrf24Base):
    def __init__(self):
        super(Nrf24Scanner, self).__init__('./nrf24-scanner.py')

        # Parse command line arguments and initialize the radio
        self.enable_prefix_address()
        self.enable_dwell_time()
        self.parse_and_init()
        
    def execute(self):
        # Put the radio in promiscuous mode
        self.radio.enter_promiscuous_mode(self.prefix_address)

        # Set the initial channel
        self.radio.set_channel(self.channels[0])

        # Sweep through the channels and decode ESB packets in pseudo-promiscuous mode
        last_tune = time.time()
        channel_index = 0
        while True:
            # Increment the channel
            if len(self.channels) > 1 and time.time() - last_tune > self.dwell_time:
                channel_index = (channel_index + 1) % (len(self.channels))
                self.radio.set_channel(self.channels[channel_index])
                last_tune = time.time()

            # Receive payloads
            value = self.radio.receive_payload()
            if len(value) >= 5:
                # Split the address and payload
                address, payload = value[0:5], value[5:]

                # Log the packet
                logging.info('{0: >2}  {1: >2}  {2}  {3}'.format(
                    self.channels[channel_index],
                    len(payload),
                    ':'.join('{:02X}'.format(b) for b in address),
                    ':'.join('{:02X}'.format(b) for b in payload)))


if __name__ == "__main__":
    Nrf24Scanner().execute()
