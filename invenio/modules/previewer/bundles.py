# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014 CERN.
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

"""Previewer bundles."""

from invenio.ext.assets import Bundle


pdfjs = Bundle(
    "vendors/jquery/dist/jquery.js",
    "vendors/pdfjs-build/generic/web/compatibility.js",
    "vendors/pdfjs-build/generic/web/l10n.js",
    "vendors/pdfjs-build/generic/build/pdf.js",
    "vendors/pdfjs-build/generic/web/viewer.js",
    filters="uglifyjs",
    output="previewer/pdfjs.js",
    weight=20,
    bower={
        "pdfjs-build": "git://github.com/bouzlibop/pdfjs-build"
    }
)

pdftk = Bundle(
    "js/previewer/pdf_viewer.js",
    filters="uglifyjs",
    output="previewer/pdftk.js",
    weight=20
)

pdfjscss = Bundle(
    "css/previewer/pdfjs_shim.css",
    "vendors/pdfjs-build/generic/web/viewer.css",
    filters="cleancss",
    output="previewer/pdfjs.css",
    weight=20
)

pdftkcss = Bundle(
    "css/previewer/pdf_viewer.css",
    filters="cleancss",
    output="previewer/pdftk.css",
    weight=20
)
