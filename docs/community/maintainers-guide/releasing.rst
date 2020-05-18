..
    This file is part of Invenio.
    Copyright (C) 2020 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Releasing Invenio
=================

In general you have two types of releases:

- **Major/Minor-level release** - Often these releases add significant new
  features and needs to go through extensive testing.
- **Patch-level release** - Often these releases fix security issues or
  important bugs.

**Differences: one or many releases**

For major/minor-level releases, you'll often be working only with the
``master``-branch and only make a single PyPI release. For patch-level
releases you'll often be working with multiple maintenance branches and make
several PyPI releases for all currently maintained versions of Invenio.

Before you start
----------------
Prior to preparing a new Invenio release, please ensure you have the latest
changes for the maintenance branches and master:

1. Check that all relevant PRs have been merged, and that all relevant Invenio
   modules have been released.
1. Fetch latest changes:
    - ``git fetch inveniosoftware``
1. Checkout maintenance or master branch:
    - ``git checkout maint-<major>.<minor>``
1. Merge or reset to latest changes:
    - ``git merge --ff-only inveniosoftware/maint-<major>.<minor>``
    - or
    - ``git reset --hard inveniosoftware/maint-<major>.<minor>``

While above is not strictly necessary, it avoids situations where you local
and GitHub branches have diverged.

Patch-level release
-------------------
A lot of time patch-level releases are not necessary for the main
Invenio-package, since by patch-level releases of the underlying modules are
automatically picked up.

With patch-level releases you'll often make multiple releases and work with
multiple maintenance branches. For instance, you might merge a bug fix to
``maint-3.1``, then to ``maint-3.2`` then to ``master``.

**Checklist per maintenance release**

1. Checkout a new branch
    - ``git checkout -b rel-v<major>.<minor>.<patch>``
1. Prepare release notes in
    - In ``docs/releases/``, copy an existing patch-level release notes (e.g.
      ``docs/releases/v3.1.2.rst``).
    - Edit release notes.
    - Include the new release notes into ``docs/releases/index.rst``.
    - Check the "Maintenance policy" (e.g. correct version?).
    - Commit
1. Bump version in ``version.py``
    - Commit (message pattern: ``release: v<major>.<minor>.<patch>``).
1. Issue a pull request against the **maintenance branch** (
   ``maint-<major>.<minor>``).
1. If Travis fails:
    - Fix issue and ensure head commit is the release commit (i.e. rebase if
      necessary).
1. Merge, tag and push release:
    - ``git merge --ff-only rel-v<major>.<minor>.<patch>``
    - ``git tag v<major>.<minor>.<patch>``
    - ``git push inveniosoftware maint-<major>.<minor> v<major>.<minor>.<patch>``
1. Regularly check Travis and PyPI to ensure the release went through.


Major/minor-level release
-------------------------


Announcing release
===================

- Blog post
- Invenio-Talk Announcement
-


