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

import click
import re
import os
import score.cli.conf
from score.init import parse_config_file, init as score_init
import textwrap
import tempfile
from ._tpl import prepare, srcvalid, copy as copytpl
from ._init import ProjectNotFound


@click.group()
@click.pass_context
def main(clickctx):
    """
    Create or load your projects
    """
    conf = parse_config_file(score.cli.conf.global_file())
    if 'score.init' not in conf:
        conf['score.init'] = {}
    conf['score.init']['modules'] = 'score.projects'
    clickctx.obj['projects'] = score_init(conf).projects
    return


@main.command()
@click.option('-n', '--name')
@click.option('-p', '--package')
@click.option('-t', '--template', default='minimal')
@click.argument('folder', type=click.Path(file_okay=False, dir_okay=True))
@click.pass_context
def create(clickctx, template, folder, name=None, package=None):
    if not srcvalid(template):
        raise click.ClickException('Could not find template "%s"' % template)
    if os.path.exists(folder):
        raise click.ClickException('Folder already exists')
    if not name:
        name = os.path.basename(folder)
    if name in clickctx.obj['projects']:
        raise click.ClickException('Project %s already exists' % name)
    if not package:
        package = name
    if not re.match('^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)*$', package):
        raise click.ClickException('Invalid package name')
    package_camelcase = ''.join(map(lambda x: x[0].upper() + x[1:],
                                    package.split('.')))
    folder = os.path.abspath(folder)
    click.confirm(textwrap.dedent('''
        Will create the project folder in the following directory:
        %s
        Is that OK?
    ''' % folder).strip(), abort=True)
    with tempfile.TemporaryDirectory() as tmp:
        prepare(template, tmp)
        copytpl(tmp, folder, {
            '__PROJECT_NAME__': name,
            '__PACKAGE_NAME__': package,
            '__PACKAGE_NAME_CAMELCASE__': package_camelcase,
        })
    clickctx.obj['projects'].register(name, folder).spawn_shell()


@main.command()
@click.option('-n', '--name')
@click.argument('folder', type=click.Path(file_okay=False, dir_okay=True))
@click.pass_context
def register(clickctx, folder, name=None):
    if not name:
        name = os.path.basename(folder)
    folder = os.path.abspath(folder)
    clickctx.obj['projects'].register(name, folder)


@main.command()
@click.argument('project')
@click.pass_context
def delete(clickctx, project):
    project = _get_project(clickctx, project)
    click.confirm(textwrap.dedent('''
        Will delete the project %s at this location:
        %s
    ''' % (project.name, project.folder)).strip(), abort=True)
    clickctx.obj['projects'].delete(project)


@main.command()
@click.argument('project')
@click.argument('folder', type=click.Path(file_okay=False, dir_okay=True))
@click.pass_context
def move(clickctx, project, folder):
    project = _get_project(clickctx, project)
    if os.sep not in folder:
        folder = os.path.join(os.getcwd(), folder)
    folder = os.path.abspath(folder)
    click.confirm(textwrap.dedent('''
        Will relocate the project %s to the following path:
        %s
    ''' % (project.name, folder)).strip(), abort=True)
    clickctx.obj['projects'].relocate(project, folder)


@main.command()
@click.argument('project')
@click.argument('newname')
@click.pass_context
def rename(clickctx, project, newname):
    project = _get_project(clickctx, project)
    clickctx.obj['projects'].rename(project, newname)


@main.command()
@click.pass_context
def list(clickctx):
    for project in clickctx.obj['projects']:
        print('%s: %s' % (project.name, project.folder))


@main.command()
@click.argument('project')
@click.pass_context
def load(clickctx, project):
    _get_project(clickctx, project).spawn_shell()


def _get_project(clickctx, name):
    try:
        return clickctx.obj['projects'][name]
    except ProjectNotFound:
        raise click.ClickException('No project called "%s"' % name)


if __name__ == '__main__':
    main()
