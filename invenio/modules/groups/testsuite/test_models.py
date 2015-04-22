# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


""" Test groups data models. """

from __future__ import absolute_import, print_function, unicode_literals

from sqlalchemy.exc import IntegrityError

from invenio.ext.sqlalchemy import db
from invenio.testsuite import make_test_suite, run_test_suite, InvenioTestCase


class BaseTestCase(InvenioTestCase):

    """Base test case."""

    def setUp(self):
        """Clear tables."""
        from invenio.modules.groups.models import Group, Membership, GroupAdmin
        Group.query.delete()
        Membership.query.delete()
        GroupAdmin.query.delete()
        db.session.commit()

    def tearDown(self):
        """Expunge session."""
        db.session.expunge_all()


class GroupTestCase(BaseTestCase):

    """Test group data model api."""

    def test_creation(self):
        """Test creation of groups."""
        from invenio.modules.groups.models import Group, \
            GroupAdmin, SubscriptionPolicy, PrivacyPolicy

        g = Group.create(name="test")
        self.assertEqual(g.name, 'test')
        self.assertEqual(g.description, '')
        self.assertEqual(g.subscription_policy, SubscriptionPolicy.CLOSED)
        self.assertEqual(g.privacy_policy, PrivacyPolicy.ADMINS)
        self.assertEqual(g.is_managed, False)
        assert g.created
        assert g.modified
        self.assertEqual(GroupAdmin.query.count(), 0)

        g2 = Group.create(
            name="admintest",
            description="desc",
            subscription_policy=SubscriptionPolicy.OPEN,
            privacy_policy=PrivacyPolicy.PUBLIC,
            is_managed=True,
            admins=[g]
        )
        self.assertEqual(g2.name, 'admintest')
        self.assertEqual(g2.description, 'desc')
        self.assertEqual(g2.subscription_policy, SubscriptionPolicy.OPEN)
        self.assertEqual(g2.privacy_policy, PrivacyPolicy.PUBLIC)
        self.assertEqual(g2.is_managed, True)
        assert g2.created
        assert g2.modified

        # Check owners
        self.assertEqual(GroupAdmin.query.count(), 1)
        admin = g2.admins[0]
        self.assertEqual(admin.admin_type, 'Group')
        self.assertEqual(admin.admin_id, g.id)

    def test_creation_signals(self):
        """Test signals sent after creation."""
        from invenio.modules.groups.models import Group
        from invenio.modules.groups.signals import group_created

        Group.called = False

        def _receiver(sender=None, group=None):
            Group.called = True
            assert sender == Group
            assert group.name == 'signaltest'

        with group_created.connected_to(_receiver):
            Group.create(name="signaltest")
        assert Group.called

        Group.called = False
        with group_created.connected_to(_receiver):
            self.assertRaises(IntegrityError, Group.create, name="signaltest")
        assert not Group.called

    def test_creation_existing_name(self):
        """Test what happens if group with identical name is created."""
        from invenio.modules.groups.models import Group, GroupAdmin

        g = Group.create(name="test", )
        self.assertEqual(GroupAdmin.query.count(), 0)
        self.assertRaises(
            IntegrityError,
            Group.create, name="test", admins=[g])
        self.assertEqual(GroupAdmin.query.count(), 0)

    def test_creation_invalid_data(self):
        """Test what happens if group with identical name is created."""
        from invenio.modules.groups.models import Group
        self.assertRaises(
            AssertionError,
            Group.create, name="")
        self.assertRaises(
            AssertionError,
            Group.create, name="test", privacy_policy='invalid')
        self.assertRaises(
            AssertionError,
            Group.create, name="test", subscription_policy='invalid')
        self.assertEqual(Group.query.count(), 0)

    def test_creation_double_admin(self):
        """Test what happens if group with identical name is created."""
        from invenio.modules.groups.models import Group, GroupAdmin

        g1 = Group.create(name="test")
        Group.create(name="doubleadmin", admins=[g1, g1])
        self.assertEqual(GroupAdmin.query.count(), 1)
        self.assertEqual(Group.query.count(), 2)

    def test_query_by_names(self):
        """Test query by names."""
        from invenio.modules.groups.models import Group

        Group.create(name="test1")
        Group.create(name="test2")
        Group.create(name="test3")

        self.assertEqual(Group.query_by_names(["invalid"]).count(), 0)
        self.assertEqual(Group.query_by_names(["test1"]).count(), 1)
        self.assertEqual(Group.query_by_names(["test2", "invalid"]).count(), 1)
        self.assertEqual(Group.query_by_names(["test1", "test2"]).count(), 2)
        self.assertEqual(Group.query_by_names([]).count(), 0)

    def test_get_by_name(self):
        """Test get by name."""
        from invenio.modules.groups.models import Group

        Group.create(name="test1")
        Group.create(name="test2")

        self.assertEqual(Group.get_by_name("test1").name, "test1")
        self.assertIsNone(Group.get_by_name("invalid"),)

    def test_delete(self):
        """Test delete."""
        from invenio.modules.groups.models import Group, GroupAdmin, Membership

        g1 = Group.create(name="test1")
        g2 = Group.create(name="test2", admins=[g1])

        # Group is admin of another group, which will be left without admins
        g1.delete(force=True)
        self.assertEqual(Group.query.count(), 1)
        self.assertEqual(GroupAdmin.query.count(), 0)
        self.assertEqual(Membership.query.count(), 1)

        g2.delete()
        self.assertEqual(Group.query.count(), 0)
        self.assertEqual(GroupAdmin.query.count(), 0)
        self.assertEqual(Membership.query.count(), 0)

    def test_add_member(self):
        pass


class MembershipTestCase(BaseTestCase):

    """Test of membership data model."""

    def test_get_by(self):
        # TEST subscribe the same person twice, invite same person twice.
        pass


TEST_SUITE = make_test_suite(GroupTestCase, MembershipTestCase)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
