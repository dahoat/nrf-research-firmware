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

from nrf24_base import Nrf24Base


class Nrf24ContinuousToneTest(Nrf24Base):
    def __init__(self):
        super(Nrf24ContinuousToneTest, self).__init__('./nrf24-continuous-tone-test.py')

        # Parse command line arguments and initialize the radio
        self._init_args('./nrf24-continuous-tone-test.py')
        self.parse_and_init()

    def execute(self):
        # Set the initial channel
        self.radio.set_channel(self.channels[0])

        # Put the radio in continuous tone test mode
        self.radio.enter_tone_test_mode()

        # Run indefinitely
        while True:
            pass


if __name__ == '__main__':
    Nrf24ContinuousToneTest().execute()
