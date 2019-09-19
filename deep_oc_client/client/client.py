# -*- coding: utf-8 -*-

# Copyright 2019 Spanish National Research Council (CSIC)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import copy
import functools
import hashlib
import json
import logging
import os
import os.path
import sqlite3
import time
import yaml

import requests
from six.moves.urllib import parse

from deep_oc_client.client import modules
from deep_oc_client import exceptions
from deep_oc_client import version


class _JSONEncoder(json.JSONEncoder):

    def default(self, o):
        return super(_JSONEncoder, self).default(o)


def cache_request(f):
    """Decorator to cache requests."""

    @functools.wraps(f)
    def wrapper(self, url, method, **kwargs):
        if method.lower() == "get":
            cache_db = os.path.join(self.cache_dir, "cache")
            try:
                conn = sqlite3.connect(cache_db)
                with conn:
                    conn.execute(
                        "CREATE TABLE IF NOT EXISTS module "
                        "    (id INTEGER PRIMARY KEY, "
                        "     url TEXT UNIQUE, "
                        "     metadata TEXT, "
                        "     timestamp REAL"
                        "    )")
                    row = conn.execute(
                        "SELECT metadata, timestamp "
                        "FROM module "
                        "WHERE url = ?", (url,)).fetchone()

                    now = time.time()

                    if not row or now - row[1] > self.cache_seconds:
                        resp, content = f(self, url, method, **kwargs)
                        if not row:
                            conn.execute(
                                "INSERT INTO module "
                                "(url, metadata, timestamp) "
                                "VALUES (?, ?, ?)",
                                (url, self._json.encode(content), now))
                        else:
                            conn.execute(
                                "UPDATE module SET"
                                "   metadata = ?, timestamp = ? "
                                "WHERE url = ?",
                                (self._json.encode(content), now, url))
                    else:
                        resp = requests.Response
                        resp.status_code = 200
                        content = json.loads(row[0])

            except sqlite3.Error as e:
                raise e
            finally:
                conn.close()
            return resp, content
        else:
            return f(self, url, method, **kwargs)

    return wrapper


class DeepOcClient(object):
    """The DEEP OC client class."""

    _catalog_url = ("https://raw.githubusercontent.com/deephdc/"
                    "deephdc.github.io/pelican/project_apps.yml")

    def __init__(self, cache=300, state_dir="~/.deep-oc/", debug=False):
        """Initialization of DeepOcClient object.

        :param bool debug: whether to enable debug logging
        """

        self.url = None

        self.http_debug = debug

        self._modules = modules.Modules(self)

        self._logger = logging.getLogger(__name__)

        if self.http_debug:
            # Logging level is already set on the root logger
            ch = logging.StreamHandler()
            self._logger.addHandler(ch)
            self._logger.propagate = False
            if hasattr(requests, 'logging'):
                rql = requests.logging.getLogger(requests.__name__)
                rql.addHandler(ch)
                # Since we have already setup the root logger on debug, we
                # have to set it up here on WARNING (its original level)
                # otherwise we will get all the requests logging messages
                rql.setLevel(logging.WARNING)

        self._json = _JSONEncoder()
        self.session = requests.Session()

        self.cache_seconds = cache

        self.state_dir = state_dir
        self.cache_dir = None
        self.init_state_dir()

    @property
    def modules(self):
        """Interface to query for modules.

        :return: Modules interface.
        :rtype: deep_oc_client.client.modules.Modules
        """
        return self._modules

    def init_state_dir(self):
        self.state_dir = os.path.expanduser(self.state_dir)
        self.cache_dir = os.path.join(self.state_dir, "cache")
        for d in (".", ):
            d = os.path.join(self.state_dir, d)
            if os.path.exists(d):
                if not os.path.isdir(d):
                    raise exceptions.ClientException(
                        message="Cannot use %s, is not a directory" % d
                    )
            else:
                os.mkdir(d)

    @cache_request
    def request(self, url, method, json=None, **kwargs):
        """Send an HTTP request with the specified characteristics.

        Wrapper around `requests.Session.request` to handle tasks such as
        setting headers, JSON encoding/decoding, and error handling.

        Arguments that are not handled are passed through to the requests
        library.

        :param str url: Path or fully qualified URL of the HTTP request. If
                        only a path is provided then the URL will be prefixed
                        with the attribute self.url. If a fully qualified URL
                        is provided then self.url will be ignored.
        :param str method: The http method to use. (e.g. 'GET', 'POST')
        :param json: Some data to be represented as JSON. (optional)
        :param kwargs: any other parameter that can be passed to
                       :meth:`requests.Session.request` (such as `headers`).
                       Except:

                       - `data` will be overwritten by the data in the `json`
                         param.
                       - `allow_redirects` is ignored as redirects are handled
                         by the session.

        :returns: The response to the request.
        """

        method = method.lower()

        kwargs.setdefault('headers', kwargs.get('headers', {}))

        kwargs["headers"]["User-Agent"] = "orpy-%s" % version.user_agent
        kwargs["headers"]["Accept"] = "application/json"

        if json is not None:
            kwargs["headers"].setdefault('Content-Type', 'application/json')
            kwargs['data'] = self._json.encode(json)

        url = parse.urljoin(self.url, url)

        self.http_log_req(method, url, kwargs)

        resp = self.session.request(method, url, **kwargs)

        self.http_log_resp(resp)

        if resp.status_code >= 400:
            raise exceptions.from_response(resp, resp.json(), url, method)

        try:
            content = resp.json().get("content", resp.json())
        except Exception:
            content = yaml.safe_load(resp.text)

        return resp, content

    def _get_links_from_response(self, response):
        d = {}
        for link in response.json().get("links", []):
            d[link["rel"]] = link["href"]
        return d.get("self"), d.get("next"), d.get("last")

    def http_log_req(self, method, url, kwargs):
        if not self.http_debug:
            return

        string_parts = ['curl -g -i']

        if not kwargs.get('verify', True):
            string_parts.append(' --insecure')

        string_parts.append(" '%s'" % url)
        string_parts.append(' -X %s' % method)

        headers = copy.deepcopy(kwargs['headers'])
        self._redact(headers, ['Authorization'])
        # because dict ordering changes from 2 to 3
        keys = sorted(headers.keys())
        for name in keys:
            value = headers[name]
            header = ' -H "%s: %s"' % (name, value)
            string_parts.append(header)

        if 'data' in kwargs:
            data = json.loads(kwargs['data'])
            string_parts.append(" -d '%s'" % json.dumps(data))
        self._logger.debug("REQ: %s" % "".join(string_parts))

    def http_log_resp(self, resp):
        if not self.http_debug:
            return

        if resp.text and resp.status_code != 400:
            try:
                body = json.loads(resp.text)
                self._redact(body, ['access', 'token', 'id'])
            except ValueError:
                body = None
        else:
            body = None

        self._logger.debug("RESP: [%(status)s] %(headers)s\nRESP BODY: "
                           "%(text)s\n", {'status': resp.status_code,
                                          'headers': resp.headers,
                                          'text': json.dumps(body)})

    def _redact(self, target, path, text=None):
        """Replace the value of a key in `target`.

        The key can be at the top level by specifying a list with a single
        key as the path. Nested dictionaries are also supported by passing a
        list of keys to be navigated to find the one that should be replaced.
        In this case the last one is the one that will be replaced.

        :param dict target: the dictionary that may have a key to be redacted;
                            modified in place
        :param list path: a list representing the nested structure in `target`
                          that should be redacted; modified in place
        :param string text: optional text to use as a replacement for the
                            redacted key. if text is not specified, the
                            default text will be sha1 hash of the value being
                            redacted
        """

        key = path.pop()

        # move to the most nested dict
        for p in path:
            try:
                target = target[p]
            except KeyError:
                return

        if key in target:
            if text:
                target[key] = text
            elif target[key] is not None:
                # because in python3 byte string handling is ... ug
                value = target[key].encode('utf-8')
                sha1sum = hashlib.sha1(value)  # nosec
                target[key] = "{SHA1}%s" % sha1sum.hexdigest()

    def head(self, url, **kwargs):
        """Perform a HEAD request.

        This calls :py:meth:`.request()` with ``method`` set to ``HEAD``.
        """
        return self.request(url, 'HEAD', **kwargs)

    def get(self, url, **kwargs):
        """Perform a GET request.

        This calls :py:meth:`.request()` with ``method`` set to ``GET``.
        """
        return self.request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        """Perform a POST request.

        This calls :py:meth:`.request()` with ``method`` set to ``POST``.
        """
        return self.request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        """Perform a PUT request.

        This calls :py:meth:`.request()` with ``method`` set to ``PUT``.
        """
        return self.request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        """Perform a DELETE request.

        This calls :py:meth:`.request()` with ``method`` set to ``DELETE``.
        """
        return self.request(url, 'DELETE', **kwargs)

    def patch(self, url, **kwargs):
        """Perform a PATCH request.

        This calls :py:meth:`.request()` with ``method`` set to ``PATCH``.
        """
        return self.request(url, 'PATCH', **kwargs)
