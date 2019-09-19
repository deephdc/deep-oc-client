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

from cliff import lister
from cliff import show


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


class ModuleShow(show.ShowOne):
    """Show metadata about a module in the DEEP Open Catalog."""

    def get_parser(self, prog_name):
        parser = super(ModuleShow, self).get_parser(prog_name)
        parser.add_argument("url",
                            metavar="<module url>",
                            help="Module URL to show")
        parser.add_argument("-r", "--raw",
                            action="store_true",
                            default=False,
                            help="Include Raw metadata in the output.")
        parser.add_argument("-t", "--tosca",
                            action="store_true",
                            default=False,
                            help="Include TOSCA template information.")
        return parser

    def take_action(self, parsed_args):
        ret = self.app.client.modules.show(parsed_args.url)
        if parsed_args.raw:
            ret["raw_metadata"] = copy.deepcopy(ret)

        ci = ret.pop("continuous_integration")
        resp, status = self.app.client.get(ci["build_status_url"] +
                                           "/lastBuild/api/json")

        if resp.ok:
            status = status["result"].upper()
        else:
            status = "NOT AVAILABLE"

        if parsed_args.formatter == "table":
            # Colors
            R = "\033[0;31;40m"  # Red
            G = "\033[0;32;40m"  # Green
            Y = "\033[0;33;40m"  # Yellow
            N = "\033[0m"  # Reset
            if status == "SUCCESS":
                status = G + status
            elif status == "FAILED":
                status = R + status
            else:
                status = Y + status
            status = status + N

        ret["build_status"] = status

        tosca = ret.pop("tosca", None)
        ret["TOSCA_template"] = "Yes" if tosca else "No"
        if tosca and parsed_args.tosca:
            for t in tosca:
                ret["%s TOSCA template" % t["title"]] = t["url"]
                ret["%s TOSCA template inputs" % t["title"]] = t["inputs"]

        sources = ret.pop("sources")
        sources["model_source_code"] = sources.pop("code")
        ret.update(sources)
        ret.pop("description")
        return self.dict2columns(ret)
