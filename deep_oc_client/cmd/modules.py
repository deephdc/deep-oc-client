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

from cliff import lister


class ModuleList(lister.Lister):
    """List existing modules at the DEEP Open Catalog."""

    def get_parser(self, prog_name):
        parser = super(ModuleList, self).get_parser(prog_name)
        parser.add_argument("-l", "--long",
                            action="store_true",
                            dest="long_output",
                            help="Show long information when listing modules")
        return parser

    def take_action(self, parsed_args):
        ret = self.app.client.modules.list()

        if not parsed_args.long_output:
            columns = (
                "Title",
                "DockerHub container",
                "url",
                "License"
            )

            values = [
                (
                    k.get("title"),
                    k.get("sources", {}).get("docker_registry_repo"),
                    k.get("url"),
                    k.get("license")
                ) for k in ret.values()
            ]
        else:
            columns = (
                "Title",
                "DockerHub container",
                "Summary",
                "Url",
                "Model code",
                "License"
            )

            values = [
                (
                    k.get("title"),
                    k.get("sources", {}).get("docker_registry_repo"),
                    k.get("summary", ""),
                    k.get("url"),
                    k.get("sources", {}).get("code"),
                    k.get("license")
                ) for k in ret.values()
            ]

        return columns, values
