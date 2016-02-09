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


@click.group()
def main():
    pass


@main.command()
@click.argument('name')
@click.pass_context
def create(clickctx, name):
    project = clickctx.obj['conf'].load('project')
    project.create(name)


@main.command()
@click.pass_context
def list(clickctx):
    project = clickctx.obj['conf'].load('project')
    for project in project.all():
        print(project.name)


@main.command()
@click.argument('name')
@click.pass_context
def load(clickctx, name):
    project = clickctx.obj['conf'].load('project')
    project.workon(name)


if __name__ == '__main__':
    main()
