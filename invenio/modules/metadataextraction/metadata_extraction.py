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


from extractors import (
    CrossRefExtractor,
    # DoiExtractor,
    DataciteExtractor,
    DoiExtractorText,
    XmpExtractor
)
from text_reader import TextReader
from utils import DoiRegistrationAgency


class MetadataExtraction(object):

    """Metadata extraction."""

    def __init__(self, file_path, use_xmp=False):
        """Initialization.

        :param file_path: a file's absolute path
        """
        self.file_path = file_path
        self.use_xmp = use_xmp
        self.xmp_extractor = XmpExtractor(full_file_path=file_path)
        self.xmp_metadata = dict()
        self.reg_agency = ""
        self.cref_extractor = None
        self.cref_metadata = dict()
        self.dc_extractor = None
        self.dc_metadata = dict()
        self.text_reader = TextReader(self.file_path)

    def _mine_pdf_file(self):
        if self.text_reader.can_open_file() is True:
                lines = self.text_reader.get_lines()
                text = ' '.join(lines)
                doi_extractor = DoiExtractorText(text=text)
                doi_list = doi_extractor.get_all_dois()
                if doi_list:
                    for doi in doi_list:
                        self.reg_agency = DoiRegistrationAgency(doi=doi).agency_id()
                        if self.reg_agency == 'datacite':
                            self.dc_extractor = DataciteExtractor(doi=doi)
                            self.dc_metadata = self.dc_extractor.get_datacite_metadata()
                            if not self.dc_metadata:
                                continue
                            else:
                                # dc_metadata should be first validated
                                return self.dc_metadata
                        elif self.reg_agency == 'crossref':
                            self.cref_extractor = CrossRefExtractor(doi=doi)
                            if not self.cref_extractor.problem_with_connection():
                                self.cref_metadata = self.cref_extractor.parse_metadata()
                            if not self.cref_metadata:
                                continue
                            else:
                                # validate non-empty meta-data
                                v = CrossRefExtractor.validate
                                if v(lines, self.cref_metadata, 0.8):
                                    return self.cref_metadata
                                else:
                                    continue
                        else:
                            continue
                else:
                    return {}
        else:
            return {}

    def _extract(self):
        """The Metadata extraction algorithm."""
        if self.xmp_extractor.can_open_file() is True:
            self.xmp_metadata = self.xmp_extractor.parse_metadata()
            if self.xmp_extractor.doi_is_present() is True:
                doi = self.xmp_extractor.get_doi()
                self.reg_agency = DoiRegistrationAgency(doi=doi).agency_id()
                if self.reg_agency == 'datacite':
                    self.dc_extractor = DataciteExtractor(doi=doi)
                    self.dc_metadata = self.dc_extractor.get_datacite_metadata()
                    return self.dc_metadata
                elif self.reg_agency == 'crossref':
                    self.cref_extractor = CrossRefExtractor(doi=doi)
                    if self.cref_extractor.problem_with_connection() is False:
                        self.cref_metadata = self.cref_extractor.parse_metadata()
                        return self.cref_metadata
                else:
                    return {}
            else:
                return self._mine_pdf_file()
        else:
            return self._mine_pdf_file()

    def get_metadata(self):
        metadata = self._extract()
        if self.reg_agency == 'crossref':
            if 'crossref_DOI' in metadata:
                metadata['doi'] = metadata['crossref_DOI']
                del metadata['crossref_DOI']
            if 'crossref_title' in metadata:
                metadata['title'] = metadata['crossref_title']
                del metadata['crossref_title']
            if 'crossref_author' in metadata:
                metadata['author'] = metadata['crossref_author']
                del metadata['crossref_author']
            if 'crossref_editor' in metadata:
                metadata['author'] = metadata['crossref_editor']
                del metadata['crossref_author']
            if 'crossref_subject' in metadata:
                metadata['subject'] = metadata['crossref_subject']
                del metadata['crossref_subject']
            if 'crossref_publisher' in metadata:
                metadata['publisher'] = metadata['crossref_publisher']
                del metadata['crossref_publisher']
            if 'crossref_type' in metadata:
                metadata['type'] = metadata['crossref_type']
                del metadata['crossref_type']
            if 'crossref_issue' in metadata:
                metadata['issue'] = metadata['crossref_issue']
                del metadata['crossref_issue']
            if 'crossref_volume' in metadata:
                metadata['volume'] = metadata['crossref_volume']
                del metadata['crossref_volume']
            if 'crossref_ISSN' in metadata:
                metadata['issn'] = metadata['crossref_ISSN']
                del metadata['crossref_ISSN']
            if 'crossref_ISBN' in metadata:
                metadata['ISBN'] = metadata['crossref_ISBN']
                del metadata['crossref_ISBN']
            if 'crossref_reference-count' in metadata:
                metadata['reference-count'] = metadata['crossref_reference-count']
                del metadata['crossref_reference-count']
            if 'crossref_journal' in metadata:
                metadata['journal'] = metadata['crossref_journal']
                del metadata['crossref_journal']
        elif self.reg_agency == '':
            metadata = dict()
        # no need to copy fields in case of datacite
        if (self.xmp_metadata and self.use_xmp):
            # validate the xmp metadata and if ok stick them to metadata
            lines = self.text_reader.get_lines()
            if lines:
                if XmpExtractor.validate(lines, self.xmp_metadata, 0.8):
                    # stick the XMP metadata to the metadata dictionary
                    for key in self.xmp_metadata:
                        metadata[key] = self.xmp_metadata[key]
        self._clear_data_structures()
        return metadata

    def _clear_data_structures(self):
        if self.xmp_metadata:
            self.xmp_metadata = dict()
        if self.dc_metadata:
            self.dc_metadata = dict()
        if self.cref_metadata:
            self.cref_metadata = dict()
