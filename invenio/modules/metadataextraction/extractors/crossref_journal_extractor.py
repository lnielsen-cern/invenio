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

import json
import urllib


class CrossrefJournalExtractor(object):

    crossref_journals_url = "http://api.crossref.org/journals/"

    def __init__(self, issn):
        self.issn = issn
        self.journal_json_data = {}
        self.journal_data = {}
        self._connect_and_read()

    def _connect_and_read(self):
        query = self.crossref_journals_url + self.issn
        # query = query.encode('utf8')
        connection = None
        try:
            connection = urllib.urlopen(query)
            response = connection.read()
            if response == 'Resource not found.':
                # probably got 'Resource not found.'
                self.journal_json_data = {}
            else:
                self.journal_json_data = json.loads(response)
        except Exception:
            print("crossref error when connecting/reading")
            self.journal_json_data = {}
        finally:
            if connection:
                connection.close()

    def problem_with_connection(self):
        if not self.journal_json_data:
            return True
        return False

    def process_journal_json_data(self):
        # do not process everything
        # just name and publisher of journal
        if (self.problem_with_connection() or
                self.journal_json_data['status'] != 'ok'):
            return {}

        important_data = self.journal_json_data['message']
        # title is a string(unicode)
        if 'title' in important_data:
            title = important_data['title']
            if not isinstance(title, unicode):
                title = title.decode('utf8')
            self.journal_data['cref_journal-title'] = title
        # publisher is a string(unicode)
        if 'publisher' in important_data:
            publisher = important_data['publisher']
            if not isinstance(publisher, unicode):
                publisher = publisher.decode('utf8')
            self.journal_data['cref_journal-publisher'] = publisher
        # ISSN is a list of strings(unicodes)
        if 'ISSN' in important_data:
            issn_list = important_data['ISSN']
            for issn_index in range(len(issn_list)):
                issn = issn_list[issn_index]
                if not isinstance(issn, unicode):
                    issn = issn.decode('utf8')
                issn_list[issn_index] = issn
            self.journal_data['cref_journal-ISSN'] = issn_list
        return self.journal_data
