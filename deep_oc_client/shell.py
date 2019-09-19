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

import argparse
import sys

from cliff import app
from cliff import commandmanager
from cliff import help

from deep_oc_client.client import client
from deep_oc_client import version


class DeepOcApp(app.App):
    """Command line client for the DEEP Open Catalog (DEEP OC).

    boilerplate text
    """

    def __init__(self):
        self.client = None

        cm = commandmanager.CommandManager('deep_oc.cli')

        super(DeepOcApp, self).__init__(
            description="Command line client for the DEEP Open Catalog",
            version=version.__version__,
            command_manager=cm,
            deferred_help=True)

    def initialize_app(self, argv):
        if self.client is None:
            self.client = client.DeepOcClient()

    def prepare_to_run_command(self, cmd):
        if isinstance(cmd, help.HelpCommand):
            return

    def build_option_parser(self, description, version):
        parser = super(DeepOcApp, self).build_option_parser(
            self.__doc__,
            version,
            argparse_kwargs={
                "formatter_class": argparse.RawDescriptionHelpFormatter,
            })
        return parser


def main(argv=sys.argv[1:]):
    app = DeepOcApp()
    return app.run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))