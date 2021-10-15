# This file is a part of Classe Viva Python API
#
# Copyright (c) 2017 The Classe Viva Python API Authors (see AUTHORS)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
import re
import requests

from datetime     import datetime
from json.decoder import JSONDecodeError
from urllib.parse import quote_plus

from .errors import AuthenticationFailedError, NotLoggedInError, NoAttachmentsError


class Session:
    """
    Spaggiari Session
    """

    base_url = "https://web.spaggiari.eu/rest/v1"

    def __init__(self, username: str = None, password: str = None):
        self.logged_in  = False
        self.first_name = None
        self.last_name  = None
        self.id         = None

        self.username = username
        self.password = password
        self.token    = None

        self.session = requests.Session()

        self.session.headers["User-Agent"] = "zorro/1.0"
        self.session.headers["Z-Dev-Apikey"] = "+zorro+"
        self.session.headers["Content-Type"] = "application/json"

    def _convert_dt(self, dt):
        """
        Utility function to corretly format date
        """
        return dt.strftime("%Y%m%d")

    def login(self, username: str = None, password: str = None):
        """
        Login to Classe Viva API
        :param username: Classe Viva username or email
        :param password: Classe Viva password
        :type username: str
        :type password: str
        :return: ID, first name and last name
        :rtype: dict
        """

        r = self.session.post(
            url=self.base_url + "/auth/login/",
            json={
                "uid" : username if username else self.username,
                "pass": password if username else self.password,
            }
        ).json()

        if 'authentication failed' in r.get('error', ''):
            raise AuthenticationFailedError()

        self.logged_in  = True
        self.first_name = r['firstName']
        self.last_name  = r['lastName']
        self.token      = r['token']
        self.id         = re.sub(r"\D", "", r['ident'])

        return {
            "id"        : self.id,
            "first_name": self.first_name,
            "last_name" : self.last_name,
        }

    def logout(self):
        """
        Logout from Classe Viva API
        """
        self.logged_in  = False
        self.first_name = None
        self.last_name  = None
        self.token      = None

    def _request(self, *path, **kargs):
        r = self._raw_request(*path, **kargs).json()

        if 'auth token expired' in r.get('error', ''):
            self.login()
            return _request(*path, **kargs)

        return r

    def _raw_request(self, *path, **kargs):
        if not self.logged_in:
            raise NotLoggedInError()

        url = self.base_url + '/' + 'students' + '/' + self.id
        for i in path:
            url += '/' + quote_plus(str(i)) if i else ''

        method_to_func = {
            'GET' : self.session.get,
            'POST': self.session.post
        }

        return method_to_func[kargs.get('method', "GET")](
            url=url,
            headers={
                "Z-Auth-Token": self.token,
            })

    def absences(self, begin=None, end=None):
        """
        Get the student's absences
        :param begin: datetime object of start date (optional)
        :param end: datetime object of end date (optional)
        :type begin: datetime
        :type end: datetime
        :return: student's absences
        :rtype: dict
        """
        return self._request(
            'absences',
            'details',
            self._convert_dt(begin) if begin else None,
            self._convert_dt(end)   if end   else None)

    def agenda(self, begin, end, event_filter='all'):
        """
        Get the student's agenda
        :param begin: datetime object of start date
        :param end: datetime object of end date
        :param event_filter: filter events by type, "all" / "homework" / "other" (optional, default "all")
        :type begin: datetime
        :type end: datetime
        :type event_filter: str
        :return: student's absences
        :rtype: dict
        """
        repr = {
            'all'     : 'all',
            'homework': 'AGHW',
            'other'   : 'AGNT'
        }

        return self._request(
            'agenda',
            repr[event_filter],
            self._convert_dt(begin),
            self._convert_dt(end))

    def didactics(self):
        """
        Get the student's educational files list
        :return: student's educational files list
        :rtype: dict
        """
        return self._request('didactics')

    def download_didactics_item(self, item):
        if item['objectType'] == 'file':
            return self._raw_request('didactics', 'item', item['contentId']).content
        elif item['objectType'] == 'link':
            return self._request('didactics', 'item', item['contentId'])['item']['link']

    def documents(self):
        """
        Get the student's documents
        :return student's documents
        :rtype: dict
        """
        return self._request('documents', method='POST')

    def download_document(self, document):
        """
        Download document
        :return: document
        :rtype: bytes
        """
        if self._request('documents', 'check', document['hash'])['document']['available']:
            return self._raw_request('documents', 'read', document['hash']).content

    def noticeboard(self):
        """
        Get the student's noticeboard
        :return: student's noticeboard
        :rtype: dict
        """
        return self._request('noticeboard')

    def download_notice(self, notice):
        """
        Download notice's attachment
        :return: attachment
        :rtype: bytes
        """
        if not len(notice['attachments']):
            raise NoAttachmentError()

        self._request('noticeboard', 'read', notice['evtCode'], notice['pubId'], '101')
        return self._raw_request(
            'noticeboard',
            'attach',
            notice['evtCode'],
            notice['pubId'],
            '101').content

    def schoolbooks(self):
        """
        Get the student's schoolbooks
        :return: student's schoolbooks
        :rtype: dict
        """
        return self._request('schoolbooks')

    def calendar(self):
        """
        Return the school calendar
        :return: school calendar
        :rtype: dict
        """
        return self._request('calendar', 'all')

    def cards(self):
        """
        Get the student's cards
        :return: student's cards
        :rtype: dict
        """
        return self._request('cards')

    def grades(self, subject=None):
        """
        Get the student's grades
        :param subject: filter results by subject (optional)
        :type subject: str
        :return: student's grades
        :rtype: dict
        """
        if not subject:
            return self._request('grades')

        return self._request('grades', 'subject', subject)

    def lessons(self, today=False, begin=None, end=None):
        """
        Get the student's lessons
        :param day: query lessons for a specific day (optional, default "today")
        :param begin: query lessons for a specific period (optional)
        :param end: query lessons for a specific period (optional)
        :type day: datetime
        :type begin: datetime
        :type end: datetime
        :return: student's lessons
        :rtype: dict
        """
        if today:
            return self._request('lessons', 'today')

        return self._request(
            'lessons',
            self.utils.convert_dt(begin),
            self.utils.convert_dt(end))

    def notes(self):
        """
        Get all of the the student's notes
        :return: student's notes
        :rtype: dict
        """
        return self._request('notes', 'all')

    def periods(self):
        """
        Get the student's periods
        :return: student's periods
        :rtype: dict
        """
        return self._request('periods')

    def subjects(self):
        """
        Get all of the student's subjects and teachers
        :return: student's subjects and teachers
        :rtype: dict
        """
        return self._request('subjects')
