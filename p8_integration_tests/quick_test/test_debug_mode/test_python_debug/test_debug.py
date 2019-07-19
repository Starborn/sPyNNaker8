# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from p8_integration_tests.quick_test.test_debug_mode.check_debug import (
    CheckDebug)


class TestDebug(CheckDebug):

    def debug_no_zero(self):
        self.debug(False)

    def test_debug_no_zero(self):
        self.runsafe(self.debug_no_zero)

    def debug_with_zero(self):
        self.debug(True)

    def test_debug_with_zero(self):
        self.runsafe(self.debug_with_zero)
