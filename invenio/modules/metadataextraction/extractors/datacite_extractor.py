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

from invenio.utils.datacite import DataciteMetadata


class DataciteExtractor(object):

    """Get meta-data for a DOI from datacite."""

    def __init__(self, doi):
        if not isinstance(doi, unicode):
            doi = doi.decode('utf-8')
        self.doi = doi
        self.dc_object = DataciteMetadata(self.doi)
        self.metadata = dict()

    def get_datacite_metadata(self):
        if not self.dc_object.error:
            # get title
            self.metadata['title'] = self.dc_object.get_titles() or ''
            # get description
            self.metadata['description'] = (
                self.dc_object.get_description() or ''
            )
            # get creators
            self.metadata['creators'] = self.dc_object.get_creators() or []
            # get publisher
            self.metadata['publisher'] = self.dc_object.get_publisher() or ''
            # get keywords/subjects
            self.metadata['subject'] = self.dc_object.get_subjects() or []
            # leave 'rights' for later because xmldict does not parse it correctly
            self.metadata['identifier'] = self.doi
        return self.metadata
