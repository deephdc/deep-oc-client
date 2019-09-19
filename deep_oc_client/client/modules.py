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


class Modules(object):

    @staticmethod
    def get_metadata_url(module):
        return "%s/raw/master/metadata.json" % module

    def __init__(self, client):
        self.client = client

    def list(self):
        resp, results = self.client.get(self.client._catalog_url)

        modules = {}
        for entry in results:
            url = self.get_metadata_url(entry["module"])
            try:
                resp, results = self.client.get(url)
            except Exception:  # nosec
                continue
            modules[entry["module"]] = results
            modules[entry["module"]]["url"] = entry["module"]

        return modules

    def show(self, module_url):
        resp, results = self.client.get(self.get_metadata_url(module_url))
        return results
