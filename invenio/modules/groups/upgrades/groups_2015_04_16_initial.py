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

import warnings
from sqlalchemy import *
from invenio.ext.sqlalchemy import db
from invenio.modules.upgrader.api import op
from sqlalchemy.dialects import mysql

# Important: Below is only a best guess. You MUST validate which previous
# upgrade you depend on.
depends_on = []


def info():
    return "Short description of upgrade displayed to end-user"


def do_upgrade():
    """Implement your upgrades here."""
    op.create_table('group',
    db.Column('id', db.Integer(15, unsigned=True), nullable=False),
    db.Column('name', db.String(length=255), server_default=u'', nullable=False),
    db.Column('description', db.Text(), nullable=True),
    db.Column('is_managed', db.Boolean(), nullable=False),
    db.Column('members_visibility', db.String(length=1), nullable=False),
    db.Column('join_policy', db.String(length=1), nullable=False),
    db.Column('created', db.DateTime(), nullable=False),
    db.Column('modified', db.DateTime(), nullable=False),
    db.PrimaryKeyConstraint('id'),
    mysql_charset='utf8',
    mysql_engine='MyISAM'
    )
    op.create_index(op.f('ix_group_name'), 'group', ['name'], unique=True)
    op.create_table('groupMEMBER',
    db.Column('id_user', db.Integer(15, unsigned=True), nullable=False),
    db.Column('id_group', db.Integer(15, unsigned=True), nullable=False),
    db.Column('state', db.String(length=1), nullable=False),
    db.Column('created', db.DateTime(), nullable=False),
    db.Column('modified', db.DateTime(), nullable=False),
    db.ForeignKeyConstraint(['id_group'], [u'group.id'], ),
    db.ForeignKeyConstraint(['id_user'], [u'user.id'], ),
    db.PrimaryKeyConstraint('id_user', 'id_group'),
    mysql_charset='utf8',
    mysql_engine='MyISAM'
    )
    op.create_table('groupADMIN',
    db.Column('id', db.Integer(15, unsigned=True), nullable=False),
    db.Column('group_id', db.Integer(15, unsigned=True), nullable=False),
    db.Column('admin_type', db.String(length=255), nullable=True),
    db.Column('admin_id', db.Integer(15, unsigned=True), nullable=True),
    db.ForeignKeyConstraint(['group_id'], [u'group.id'], ),
    db.PrimaryKeyConstraint('id', 'group_id'),
    mysql_charset='utf8',
    mysql_engine='MyISAM'
    )


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    # Example of raising errors:
    # raise RuntimeError("Description of error 1", "Description of error 2")


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    # Example of issuing warnings:
    # warnings.warn("A continuable error occurred")
