# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2011, 2012, 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Unit Tests for BibAuthority"""

from invenio.testsuite import InvenioTestCase
from invenio.testsuite import make_test_suite, run_test_suite


class TestBibAuthorityEngine(InvenioTestCase):
    """Unit tests for bibauthority_engine"""

    def test_split_name_parts(self):
        """bibauthority - test get_type_from_authority_id"""
        from invenio.legacy.bibauthority.config import CFG_BIBAUTHORITY_PREFIX_SEP
        from invenio.legacy.bibauthority.engine import get_type_from_control_no
        prefix = "JOURNAL"
        control_no = "(CERN)abcd1234" # must start with a '('
        self.assertEqual(get_type_from_control_no(
                            prefix + CFG_BIBAUTHORITY_PREFIX_SEP + control_no),
                         prefix)

TEST_SUITE = make_test_suite(TestBibAuthorityEngine)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
