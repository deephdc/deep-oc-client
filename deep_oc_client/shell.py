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
import cliff.interactive

from deep_oc_client.client import client
from deep_oc_client import version

INTRO = """
     ##         ###
     ##       ######  ##
 .#####   #####   #######.  .#####.
##   ## ## //   ##  //  ##  ##   ##
##. .##  ###  ###   // ###  ##   ##
  ## ##    ####     ####    #####.
          Hybrid-DataCloud  ##

"""

BANNER = """
    This tool will help you browsing the DEEP OC Marketplace contents
    (https://marketplace.deep-hybrid-datacloud.eu) and interact with them.
"""


class InteractiveApp(cliff.interactive.InteractiveApp):
    def cmdloop(self, *args, **kwargs):
        intro = INTRO + BANNER
        self.poutput(str(intro) + "\n")
        super(InteractiveApp, self).cmdloop(*args, **kwargs)


class DeepOcApp(app.App):
    """Command line client for the DEEP Open Catalog (DEEP OC).

    """

    def __init__(self):
        self.client = None

        cm = commandmanager.CommandManager('deep_oc.cli')

        super(DeepOcApp, self).__init__(
            description="Command line client for the DEEP Open Catalog",
            version=version.__version__,
            command_manager=cm,
            deferred_help=True)

        self.interactive_app_factory = InteractiveApp

    def initialize_app(self, argv):
        if self.client is None:
            self.client = client.DeepOcClient(
                state_dir=self.options.state_dir,
                debug=self.options.debug,
                cache=self.options.cache
            )

    def prepare_to_run_command(self, cmd):
        if isinstance(cmd, help.HelpCommand):
            return

    def build_option_parser(self, description, version):
        parser = super(DeepOcApp, self).build_option_parser(
            self.__doc__ + BANNER,
            version,
            argparse_kwargs={
                "formatter_class": argparse.RawDescriptionHelpFormatter,
            })

        parser.add_argument("-s", "--state-dir",
                            metavar="<state-directory>",
                            default="~/.deep-oc",
                            help="Directory where the DEEP OC CLI will"
                                 "maintain its status(default: ~/.deep-oc"),

        parser.add_argument("-c", "--cache",
                            metavar="<seconds>",
                            default=300,
                            type=int,
                            help="Number of seconds to cache results. Set to "
                                 "-1 to disable cache at all. Defaults to 300")
        return parser


def main(argv=sys.argv[1:]):
    app = DeepOcApp()
    return app.run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
