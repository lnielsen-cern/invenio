# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013, 2015 CERN.
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

"""WebAccount Forms."""

from flask.ext.login import current_user
from flask.ext.wtf import Form, validators

from invenio.base.globals import cfg
from invenio.base.i18n import _
from invenio.legacy.webuser import email_valid_p
from invenio.utils.forms import InvenioBaseForm

from sqlalchemy.exc import SQLAlchemyError

from wtforms.fields import BooleanField, HiddenField, PasswordField, \
    StringField, SubmitField
from wtforms.validators import DataRequired, StopValidation

from .models import User
from .validators import validate_email, validate_nickname, \
    validate_nickname_or_email, wash_login_method


def nickname_validator(form, field):
    """Validate nickname."""
    validate_nickname(field.data)
    # is nickname already taken?
    try:
        User.query.filter(User.nickname == field.data).one()
        raise validators.ValidationError(
            _("Desired nickname %(nick)s already exists in the database.",
              nick=field.data)
        )
    except SQLAlchemyError:
        pass


def email_validator(form, field):
    """Validate email."""
    field.data = field.data.lower()
    validate_email(field.data)

    # is email already taken?
    try:
        User.query.filter(User.email == field.data).one()
        raise validators.ValidationError(
            _("Supplied email address %(email)s already exists.",
              email=field.data)
        )
    except SQLAlchemyError:
        pass


def password_validator(form, field):
    """Validate password."""
    min_length = cfg['CFG_ACCOUNT_MIN_PASSWORD_LENGTH']
    if len(field.data) < min_length:
        raise validators.ValidationError(
            _("Password must be at least %(x_pass)d characters long.",
              x_pass=min_length))


def password2_validator(form, field):
    """Validate password2."""
    if field.data != form.password.data:
        raise validators.ValidationError(_("Both passwords must match."))


def current_user_validator(attr):
    """Validator to check if value is same as current_user."""
    def _validator(form, field):
        if current_user[attr] == field.data:
            raise StopValidation()
    return _validator


class LoginForm(Form):

    """Login Form."""

    nickname = StringField(
        _("Nickname"),
        validators=[DataRequired(message=_("Nickname not provided")),
                    validate_nickname_or_email])
    password = PasswordField(_("Password"))
    remember = BooleanField(_("Remember Me"))
    referer = HiddenField()
    login_method = HiddenField()
    submit = SubmitField(_("Sign in"))

    def validate_login_method(self, field):
        """Validate login_method."""
        field.data = wash_login_method(field.data)


class ChangeUserEmailSettingsForm(InvenioBaseForm):

    """Form to change user email settings."""

    email = StringField(_("New email"))

    def validate_email(self, field):
        """Validate email."""
        field.data = field.data.lower()
        if validate_email(field.data.lower()) != 1:
            raise validators.ValidationError(
                _("Supplied email address %(email)s is invalid.",
                  email=field.data)
            )

        # is email already taken?
        try:
            User.query.filter(User.email == field.data).one()
            raise validators.ValidationError(
                _("Supplied email address %(email)s already exists "
                  "in the database.", email=field.data)
            )
        except SQLAlchemyError:
            pass

        # if the email is changed we reset the password to a random one, such
        # that the user is forced to confirm the new email
        import random
        from webuser import updatePasswordUser
        updatePasswordUser(current_user['id'], int(random.random() * 1000000))

        from flask import flash, url_for
        flash(_("Note that if you have changed your email address, you \
                will have to <a href=%(link)s>reset</a> your password anew.",
                link=url_for('webaccount.lost')), 'warning')


class ProfileForm(InvenioBaseForm):

    """Profile form."""

    nickname = StringField(
        _("Username"),
        validators=[DataRequired(), current_user_validator('nickname'),
                    nickname_validator]
    )
    family_name = StringField()
    given_names = StringField()
    email = StringField(
        filters=[lambda x: x.lower(), ],
        validators=[DataRequired(), current_user_validator('email'),
                    email_validator]
    )


class LostPasswordForm(InvenioBaseForm):

    """Form to recover lost password."""

    email = StringField(
        _("Email address"),
        validators=[DataRequired(), email_validator]
    )


class ChangePasswordForm(InvenioBaseForm):

    """Form to change password."""

    current_password = PasswordField(_("Current password"),
                                     description=_("Your current password"))
    password = PasswordField(
        _("New password"),
        description=_("The password phrase may contain punctuation, "
                      "spaces, etc."))
    password2 = PasswordField(_("Confirm new password"),)

    def validate_current_password(self, field):
        """Validate current password."""
        from invenio.ext.login import authenticate
        if not authenticate(current_user['nickname'], field.data):
            raise validators.ValidationError(
                _("Password mismatch."))


class RegisterForm(Form):

    """User registration form."""

    email = StringField(
        _("Email address"),
        validators=[DataRequired(message=_("Email not provided")),
                    email_validator],
        description=_("Example") + ": john.doe@example.com")
    nickname = StringField(
        _("Nickname"),
        validators=[DataRequired(message=_("Nickname not provided")),
                    nickname_validator],
        description=_("Example") + ": johnd")
    password = PasswordField(
        _("Password"),
        description=_(
            "The password phrase may contain punctuation, spaces, etc."
        ),
        validators=[password_validator],
    )
    password2 = PasswordField(
        _("Confirm password"),
        validators=[password2_validator]
    )
    referer = HiddenField()
    action = HiddenField(default='login')
    submit = SubmitField(_("Register"))
