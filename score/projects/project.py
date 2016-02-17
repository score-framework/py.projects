# Copyright © 2015 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

import re
import os
from vex.main import _main as vex_main


def copytpl(src, dst, vars):
    if os.path.isdir(src):
        os.makedirs(dst)
        for filetpl in os.listdir(src):
            file = filetpl
            for k, v in vars.items():
                file = file.replace(k, v)
            copytpl(os.path.join(src, filetpl), os.path.join(dst, file), vars)
    else:
        try:
            content = open(src).read()
            for k, v in vars.items():
                content = content.replace(k, v)
            open(dst, 'w').write(content)
        except UnicodeDecodeError:
            # not a text file, just copy content
            open(dst, 'wb').write(open(src, 'rb').read())


class Project:

    @staticmethod
    def create(conf, id, folder, venvdir, template='web'):
        project = Project(conf, id, folder, venvdir)
        assert not project.exists, 'Project already exists'
        scaffold = os.path.join(os.path.dirname(__file__),
                                'scaffold', template, 'files')
        copytpl(scaffold, project.folder, {
            '{venv}': project.venvdir,
            '{name}': project.name,
            '{folder}': project.folder,
            '{ucname}': project.name.capitalize(),
        })
        project.recreate_venv()
        project.install()
        project.register_configurations()
        return project

    def __init__(self, conf, id, folder, venvdir):
        self.id = id
        self.conf = conf
        self.folder = folder
        self.venvdir = venvdir

    def recreate_venv(self):
        self.vex('--make', 'true')

    def install(self):
        self.vex('pip', 'install', '--editable', self.folder)

    def register_configurations(self):
        prodconf = os.path.join(self.folder, 'production.conf')
        devconf = os.path.join(self.folder, 'development.conf')
        localconf = os.path.join(self.folder, 'local.conf')
        self.vex('score', 'conf', 'add', prodconf)
        self.vex('score', 'conf', 'add', devconf)
        self.vex('score', 'conf', 'add', '-d', localconf)

    def spawn_shell(self):
        self.vex('--path', self.venvdir, '--cwd', self.folder)

    def vex(self, *args):
        environ = os.environ.copy()
        environ['VIRTUAL_ENV_NAME'] = self.name
        vex_main(environ, ('--path', self.venvdir) + args)

    @property
    def name(self):
        return os.path.basename(self.folder)

    @property
    def exists(self):
        return os.path.exists(self.folder)
