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

"""Groups data models."""

from __future__ import absolute_import, print_function, unicode_literals

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils import generic_relationship
from sqlalchemy_utils.types.choice import ChoiceType

from invenio.base.i18n import _
from invenio.ext.sqlalchemy import db
from invenio.ext.sqlalchemy.utils import session_manager
from invenio.modules.accounts.models import User

from .signals import group_created, group_deleted


class SubscriptionPolicy(object):

    """Group subscription policies."""

    OPEN = 'O'
    """Users can self-subscribe."""

    APPROVAL = 'A'
    """Users can self-subscribe but requires administrator approval."""

    CLOSED = 'C'
    """Subscription is by administrator invitation only."""

    @classmethod
    def validate(cls, policy):
        """Validate policy value."""
        return policy in [cls.OPEN, cls.APPROVAL, cls.CLOSED]


class PrivacyPolicy(object):

    """Group privacy policies."""

    PUBLIC = 'P'
    """Group membership is fully public."""

    MEMBERS = 'M'
    """Group administrators and group members can view members."""

    ADMINS = 'A'
    """Group administrators can view members."""

    @classmethod
    def validate(cls, policy):
        """Validate policy value."""
        return policy in [cls.PUBLIC, cls.MEMBERS, cls.ADMINS]


class MembershipState(object):

    """Membership state."""

    PENDING_ADMIN = 'A'
    """Pending admin verification."""

    PENDING_USER = 'U'
    """Pending user verification."""

    ACTIVE = 'M'
    """Active membership."""

    @classmethod
    def validate(cls, state):
        """Validate state value."""
        return state in [cls.ACTIVE, cls.PENDING_ADMIN, cls.PENDING_USER]


class Group(db.Model):

    """Group data model."""

    __tablename__ = 'group'  # FIXME

    PRIVACY_POLICIES = [
        (PrivacyPolicy.PUBLIC, _('Public')),
        (PrivacyPolicy.MEMBERS, _('Group members')),
        (PrivacyPolicy.ADMINS, _('Group admins')),
    ]
    """Privacy policy choices."""

    SUBSCRIPTION_POLICIES = [
        (SubscriptionPolicy.OPEN, _('Open')),
        (SubscriptionPolicy.APPROVAL, _('Open with approval')),
        (SubscriptionPolicy.CLOSED, _('Closed')),
    ]
    """Subscription policy choices."""

    id = db.Column(db.Integer(15, unsigned=True), nullable=False,
                   primary_key=True, autoincrement=True)
    """Group identifier."""

    name = db.Column(
        db.String(255), nullable=False, default='', unique=True, index=True,
        info=dict(
            description=_('Required. A name of this group.')
        ))
    """Name of group."""

    description = db.Column(
        db.Text, nullable=True, default='',
        info=dict(
            description=_('Optional. A short description of the group'
                          ' which will be displayed on the index'
                          ' page of the group.')
        ))
    """Description of group."""

    is_managed = db.Column(db.Boolean, default=False, nullable=False)
    """Determine if group is system managed."""

    privacy_policy = db.Column(
        ChoiceType(PRIVACY_POLICIES, impl=db.String(1)), nullable=False,
        default=PrivacyPolicy.ADMINS,
        name="members_visibility"  # FIXME
    )
    """Policy for who can view the list of group members."""

    subscription_policy = db.Column(
        ChoiceType(SUBSCRIPTION_POLICIES, impl=db.String(1)), nullable=False,
        default=SubscriptionPolicy.CLOSED,
        name="join_policy"  # FIXME
    )
    """Policy for how users can be subscribed to the group."""

    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    """Creation timestamp."""

    modified = db.Column(db.DateTime, nullable=False, default=datetime.now,
                         onupdate=datetime.now)
    """Modification timestamp."""

    @classmethod
    def create(cls, name=None, description='', privacy_policy=None,
               subscription_policy=None, is_managed=False, admins=None):
        """Create a new group.

        If the group is successfully created, the ``group_created`` signal will
        be sent.

        :param name: Name of group. Required and must be unique.
        :param description: Description of group. Default: ``''``.
        :param subscription_policy: Subscription
        :param admins: Mixed list of user and group objects that will become
            owners of the group.
        :returns: Group object.
        :raises: IntegrityError, AssertionError
        """
        assert name
        assert privacy_policy is None or PrivacyPolicy.validate(privacy_policy)
        assert subscription_policy is None or \
            SubscriptionPolicy.validate(subscription_policy)
        assert admins is None or isinstance(admins, list)

        try:
            obj = cls(
                name=name,
                description=description,
                privacy_policy=privacy_policy,
                subscription_policy=subscription_policy,
                is_managed=is_managed,
            )
            db.session.add(obj)

            for a in set(admins or []):
                db.session.add(GroupAdmin(group=obj, admin=a))

            db.session.commit()
            group_created.send(cls, group=obj)
            return obj
        except IntegrityError:
            # Either due to duplicate group name, or that group admin already
            # exists.
            db.session.rollback()
            raise

    def delete(self, force=False):
        """Delete a group an all associated memberships.

        If the group is successfully deleted, the ``group_deleted`` signal will
        be sent.

        :param force: Force deletion even if group is admin for another group.
        """
        try:
            # # Find groups which would be left without a GroupAdmin by
            # # deleting this group.
            # # Do we care? What if user is deleted?
            # if not force:

            #     noadmin_group_count = GroupAdmin.admins_by_group_id(
            #         filter_groups=GroupAdmin.query_by_admin(self)
            #     ).having(func.count(GroupAdmin.id) == 1).count()

            #     if noadmin_group_count > 0:
            #         raise IntegrityError("")

            Membership.query_by_group(self).delete()
            GroupAdmin.query_by_group(self).delete()
            GroupAdmin.query_by_admin(self).delete()
            db.session.delete(self)
            db.session.commit()

            group_deleted.send(self.__class__, group=self)
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def update(cls, ):
        """Create a new group."""
        pass

    @classmethod
    def query_by_names(cls, names):
        """Query group by a list of group names."""
        assert isinstance(names, list)
        return cls.query.filter(cls.name.in_(names))

    @classmethod
    def get_by_name(cls, name):
        """Query group by a list of group names."""
        try:
            return cls.query.filter_by(name=name).one()
        except NoResultFound:
            return None

    def remove_admin(self, admin):
        """Remove a user from group (independent of their membership state)."""
        return GroupAdmin.delete(self, admin)

    def add_admin(self, admin):
        """Invite a user to a group."""
        return GroupAdmin.create(admin)

    def remove_member(self, user):
        """Remove a user from group (independent of their membership state)."""
        Membership.delete(self, user)

    def add_member(self, user, state=MembershipState.ACTIVE):
        """Invite a user to a group."""
        try:
            return Membership.create(self, user)
        except IntegrityError:
            return None

    def invite(self, user, admin=None):
        """Invite a user to a group (done by admins).

        Wrapper around ``add_member()`` to ensure proper membership state.

        :param user: User to invite.
        :param admin: Admin doing the action. If provided, user is only invited
            if the object is an admin for this group. Default: None.
        """
        if admin is None or self.is_admin(admin):
            return self.add_member(user, state=MembershipState.PENDING_USER)
        return None

    def subscribe(self, user):
        """Subscribe a user to a group (done by users).

        Wrapper around ``add_member()`` which checks subscription policy.

        :param user: User to subscribe.
        """
        if self.subscription_policy == SubscriptionPolicy.OPEN:
            return self.add_member(user)
        elif self.subscription_policy == SubscriptionPolicy.APPROVAL:
            return self.add_member(user, state=MembershipState.PENDING_ADMIN)
        elif self.subscription_policy == SubscriptionPolicy.CLOSED:
            return None

    def is_admin(self, user):
        """."""

    def is_member(self, user, with_pending=False):
        """."""


class Membership(db.Model):

    """Represent a users membership of a group."""

    MEMBERSHIP_STATE = {
        MembershipState.PENDING_ADMIN: _("Pending admin approval"),
        MembershipState.PENDING_USER: _("Pending member approval"),
        MembershipState.ACTIVE: _("Active"),
    }

    __tablename__ = 'groupMEMBER'

    id_user = db.Column(db.Integer(15, unsigned=True), db.ForeignKey(User.id),
                        nullable=False, primary_key=True)
    """User for membership."""

    id_group = db.Column(
        db.Integer(15, unsigned=True), db.ForeignKey(Group.id), nullable=False,
        primary_key=True)
    """Group for membership."""

    state = db.Column(ChoiceType(MEMBERSHIP_STATE, impl=db.String(1)),
                      nullable=False)
    """State of membership."""

    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    """Creation timestamp."""

    modified = db.Column(db.DateTime, nullable=False, default=datetime.now,
                         onupdate=datetime.now)
    """Modification timestamp."""

    #
    # Relations
    #

    user = db.relationship(User, backref=db.backref(
        'groups'))

    group = db.relationship(Group, backref=db.backref(
        'members', cascade="all, delete-orphan"))

    @classmethod
    def get(cls, user, group):
        """."""
        pass

    @classmethod
    def _filter(cls, query, state=MembershipState.ACTIVE, eager=None):
        """Filter a query result."""
        # Filter by membership state
        if state is not None:
            query = query.filter(state=state)

        # Eager loading of relationships
        eager = eager or []
        for field in eager:
            query = query.options(joinedload(field))

        return query

    @classmethod
    def query_by_user(cls, user, **kwargs):
        """Get a user's memberships."""
        return cls._filter(
            cls.query.filter(id_user=user.get_id()),
            **kwargs
        )

    @classmethod
    def query_by_group(cls, group, **kwargs):
        """Get a group's members."""
        return cls._filter(
            cls.query.filter(id_group=group.id),
            **kwargs
        )

    @classmethod
    def create(cls, group, user, state=MembershipState.ACTIVE):
        """Create a new membership."""

    def delete(self):
        """Delete a membership."""

    def accept(self):
        """."""
        # Set set member

    def reject(self):
        """."""
        # Alias for delete?


# NOTE: Below database model should be refactored once the ACL system have been
# rewritten to allow efficient list queries (i.e. list me all groups i have
# permissions to)
class GroupAdmin(db.Model):

    """Represent an administrator of a group."""

    __tablename__ = 'groupADMIN'

    __table_args__ = (
        db.UniqueConstraint('group_id', 'admin_type', 'admin_id'),
        db.Model.__table_args__
    )

    id = db.Column(db.Integer(15, unsigned=True), nullable=False,
                   primary_key=True, autoincrement=True)

    group_id = db.Column(
        db.Integer(15, unsigned=True), db.ForeignKey(Group.id), nullable=False,
        primary_key=True)
    """Group for membership."""

    group = db.relationship(Group, backref=db.backref(
        'admins', cascade="all, delete-orphan"))

    admin_type = db.Column(db.Unicode(255))
    """Generic relationship to an object."""

    admin_id = db.Column(db.Integer)
    """Generic relationship to an object."""

    admin = generic_relationship(admin_type, admin_id)
    """Generic relationship to administrator of group."""

    @classmethod
    def query_by_group(cls, group):
        """Get all admins for a specific group."""
        return cls.query.filter_by(group=group)

    @classmethod
    def query_by_admin(cls, admin):
        """Get all groups for for a specific admin."""
        return cls.query.filter_by(admin=admin)

    @classmethod
    def query_admins_by_group_id(cls, filter_groups=None):
        """Get count of admins per group.

        :param groups_query: Subquery used to filter groups.
        """
        query = db.session.query(
            Group.id, func.count(GroupAdmin.id)
        ).join(
            GroupAdmin
        ).group_by(
            Group.id
        )

        if filter_groups:
            query = query.filter(Group.id.in_(filter_groups))

        return query
