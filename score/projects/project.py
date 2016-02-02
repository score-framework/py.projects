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
from score.cli.conf import confroot, addconf, setdefault
import venv
import subprocess


def copytpl(src, dst, vars):
    if os.path.isdir(src):
        os.makedirs(dst)
        for filetpl in os.listdir(src):
            file = filetpl
            for k, v in vars.items():
                file = file.replace(k, v)
            copytpl(os.path.join(src, filetpl), os.path.join(dst, file), vars)
    else:
        content = open(src).read()
        for k, v in vars.items():
            content = content.replace(k, v)
        open(dst, 'w').write(content)
    pass


class Project:

    def __init__(self, conf, name):
        assert re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name), 'Invalid name'
        self.name = name
        self.conf = conf
        self.root = os.path.join(conf.root, name)
        self.venvdir = os.path.join(confroot(), 'projects', name)

    def create(self, template='web'):
        # copy scaffold
        assert not self.exists, 'Project already exists'
        scaffold = os.path.join(os.path.dirname(__file__),
                                'scaffold', template, 'files')
        copytpl(scaffold, self.root, {
            '{venv}': self.venvdir,
            '{root}': self.root,
            '{name}': self.name,
            '{ucname}': self.name.capitalize(),
        })
        # create virtualenv
        venv.create(self.venvdir, clear=True, symlinks=False, with_pip=True)
        # register configurations
        prodconf = os.path.join(self.root, 'production.conf')
        devconf = os.path.join(self.root, 'development.conf')
        localconf = os.path.join(self.root, 'local.conf')
        addconf('production', prodconf, root=self.venvdir)
        addconf('development', devconf, root=self.venvdir)
        addconf('local', localconf, root=self.venvdir)
        setdefault('local', root=self.venvdir)
        # install the project
        python = os.path.join(self.venvdir, 'bin', 'python')
        subprocess.check_call([python, 'setup.py', 'develop'], cwd=self.root)

    @property
    def exists(self):
        return os.path.exists(self.root)
