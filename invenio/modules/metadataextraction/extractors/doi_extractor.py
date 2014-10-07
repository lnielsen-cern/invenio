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


import re
import string


class DoiExtractorText(object):

    punctuation_in_doi = {":", "/", ".", "-", "(", ")"}
    excluded_punctuation = set(string.punctuation)-punctuation_in_doi
    # doi_pattern = re.compile(
    #     '[doi|DOI][\s\.\:]{0,2}(10\.\d{4}[\d\:\.\-\/a-z]+)[A-Z\s]'
    # )
    doi_pattern = re.compile(
        '(10\.\d{4}[\d\:\.\-\/a-z]+)[A-Z\s]'
    )

    def __init__(self, text):
        # text is a string
        self.text = text
        self.all_dois = []
        self._do_extract()

    def _do_extract(self):
        parts_to_strip = ['.g0', '.s0', '.t0']
        found_dois = self.doi_pattern.search(self.text)
        if found_dois:
            for doi in found_dois.groups():
                if '10.5281' in doi or '10.5072' in doi:
                    continue
                if (doi.endswith('/') or doi.endswith('-') or
                        '0000' in doi or 'xx' in doi):
                    continue
                else:
                    for e in parts_to_strip:
                        if e in doi:
                            doi = doi.replace(doi[doi.find(e):len(doi)], "")
                    if (doi.endswith('.') or doi.endswith('-') or
                            doi.endswith(':')):
                        doi = doi[:len(doi)-1]
                    if (doi.startswith('doi:') or doi.startswith('DOI:') or
                            doi.startswith('Doi:')):
                        doi = ''.join(doi[i] for i in range(4, len(doi)))
                self.all_dois.append(doi)

    def get_all_dois(self):
        doi_list = []
        if self.all_dois:
            for e in self.all_dois:
                if e not in doi_list:
                    doi_list.append(e)
            return self.all_dois
        return []


class DoiExtractor(object):

    """Try to extract a DOI from the first lines."""

    punctuation_in_doi = {":", "/", ".", "-", "(", ")"}
    excluded_punctuation = set(string.punctuation)-punctuation_in_doi
    doi_pattern = re.compile("10[.][0-9]{4,}/")

    def __init__(self, lines_of_text, how_many_chars):
        self.lines_of_text = lines_of_text
        text = ' '.join(line for line in self.lines_of_text)
        if how_many_chars > len(text):
            how_many_chars = len(text)
        text_to_search = text[0:how_many_chars]
        self.lines_to_search = text_to_search.split()
        self.tokens = []
        self.all_dois = []
        self.__doi_extraction()

    def __process(self):
        """Process lines of text."""
        for line in self.lines_to_search:
            line = line.split()
            for t in line:
                if not isinstance(t, unicode):
                    t = t.decode('utf8')
                t = "".join(c for c in t if c not in self.excluded_punctuation)
                t.strip('')
                if (t.endswith(".")) or (t.endswith(",")) or (t.endswith(":")):
                    # copy all characters but don't include the last one
                    t = t[0:len(t)-1]
                self.tokens.append(t)

    def __process_dois(self):
        parts_to_strip = ['.g0', '.s0', '.t0']
        tmp = []
        for doi in self.all_dois:
            for e in parts_to_strip:
                if e in doi:
                    doi = doi.replace(doi[doi.find(e):len(doi)], "")
            tmp.append(doi)
        self.all_dois = []
        self.all_dois = [elem for elem in tmp]
        tmp = []
        for doi in self.all_dois:
                if doi.endswith("."):
                    # remove last dot
                    doi = "".join(doi[i] for i in range(0, len(doi)-1))
                if doi.startswith("http"):
                    tmp.append(doi)
                else:
                    if (doi.startswith("doi:")) or (doi.startswith("DOI:")) or\
                       (doi.startswith("Doi:")):
                        doi = "".join(doi[i] for i in range(4, len(doi)))
                    dx_doi_url = "http://dx.doi.org/".decode('utf8')
                    doi = dx_doi_url+doi
                    tmp.append(doi)
        self.all_dois = []
        self.all_dois = [elem for elem in tmp]
        tmp = []
        del tmp
        for doi in self.all_dois:
            if (doi.startswith("10.5281")) or (doi.startswith("10.5072")):
                self.all_dois.remove(doi)
            part_after_line = doi[doi.find('/')+1:]
            if len(part_after_line) < 3:
                self.all_dois.remove(doi)

    def __doi_extraction(self):
        self.__process()
        for t in self.tokens:
            if re.search(self.doi_pattern, t) is not None:
                if t.endswith("/") or t.endswith("-"):
                    pass
                else:
                    self.all_dois.append(t)
        self.__process_dois()

    def get_possible_doi(self):
        if len(self.all_dois) > 0:
            doi_to_return = self.all_dois[0]
            doi_to_return = doi_to_return[doi_to_return.find("10."):]
            return doi_to_return
        else:
            return None
