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

import urllib2
import json


class DoiRegistrationAgency(object):

    """Find the agency in which a DOI is registered with."""

    def __init__(self, doi):
        if not isinstance(doi, unicode):
            doi = doi.decode('utf-8')
        self.doi = doi
        self.url = 'http://api.crossref.org/works/{0}/agency'.format(self.doi)
        self.ok_status = True
        try:
            # query url and get info about agency
            data_str = urllib2.urlopen(self.url).read()
            # load read data as dictionary
            self.data = json.loads(data_str)
            if self.data['status'] != 'ok':
                self.ok_status = False
        except Exception:
            self.ok_status = False
        if self.ok_status:
            self.agency_data = self.data['message']['agency']

    def agency_id(self):
        """Get the identifier of the agency."""
        if 'id' in self.agency_data:
            return self.agency_data['id']
        return None

    def agency_label(self):
        """Get the label of the agency."""
        if 'label' in self.agency_data:
            return self.agency_data['label']
        return None
