

from collections import namedtuple
from functools import partial

from flask.ext.principal import Permission, ActionNeed


GroupCreateActionNeed = ActionNeed("groups_group_create")

GroupNeed = namedtuple('GroupNeed', ['method', 'value'])
GroupOwnerNeed = partial(GroupNeed, 'owner')
GroupMemberNeed = partial(GroupNeed, 'member')


class GroupAdministratePermission(Permission):

    """Group administration permission."""

    def __init__(self, group_id):
        """Initialize permission."""
        super(GroupAdministratePermission, self).__init__(
            GroupOwnerNeed(group_id)
        )


class GroupCreatePermission(Permission):

    """Group creation permission."""

    def __init__(self, group_id):
        """Initialize permission."""
        super(GroupCreatePermission, self).__init__(
            GroupCreateActionNeed()
        )


class GroupPermission(ACLPermission):

    """A group permission object."""

    def __init__(self, group_id):
        """Initialize permission."""
        super(GroupPermission, self).__init__(
            "group",
        )
