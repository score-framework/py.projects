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

from score.init import ConfiguredModule
from .project import Project
import os
from score.cli.conf import confroot
import configparser


defaults = {
}


def init(confdict):
    conf = defaults.copy()
    conf.update(confdict)
    return ConfiguredProjectModule()


class ConfiguredProjectModule(ConfiguredModule):

    def __init__(self):
        import score.projects
        super().__init__(score.projects)

    def get(self, name):
        try:
            return next(p for p in self if p.name == name)
        except StopIteration:
            raise ValueError('No project called "%s"' % name)

    def create(self, folder, *, template='web'):
        existing = self.all()
        name = os.path.basename(folder)
        if name in existing:
            raise ValueError('Project "%s" already exists' % name)
        id = self._new_id(existing)
        venvdir = os.path.join(confroot(global_=True), 'projects',
                               'venv', str(id))
        project = Project.create(self, id, folder, venvdir, template=template)
        settings = self._read_conf()
        settings[str(id)] = {'folder': folder}
        self._write_conf(settings)
        return project

    def all(self):
        return dict((p.name, p) for p in self)

    def __iter__(self):
        settings = self._read_conf()
        for section in settings:
            if section == 'DEFAULT':
                continue
            folder = settings[section]['folder']
            venvdir = os.path.join(confroot(global_=True), 'projects',
                                   'venv', section)
            yield(Project(self, int(section), folder, venvdir))

    __getitem__ = get

    def _new_id(self, all_projects=None):
        if all_projects is None:
            all_projects = self.all()
        id = 1
        if all_projects:
            id = 1 + max(project.id for project in all_projects.values())
        return id

    def _read_conf(self):
        root = os.path.join(confroot(global_=True), 'projects')
        settings = configparser.ConfigParser()
        settings.read(os.path.join(root, 'list.conf'))
        return settings

    def _write_conf(self, settings):
        root = os.path.join(confroot(global_=True), 'projects')
        file = os.path.join(root, 'list.conf')
        settings.write(open(file, 'w'))
