# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxy_pool
   Description :   Version minima para correr como validador efimero
                    (GitHub Actions). Solo trae los comandos "once" (un
                    ciclo de fetch+validacion, termina solo) y "fetcher"
                    (listar fuentes activas). El dashboard, la API y las
                    metricas viven aparte, en la copia privada del proyecto.
   Author :        Claude
   date：          2026/07/11
-------------------------------------------------
"""
__author__ = 'Claude'

import click
from helper.launcher import startOnce
from setting import BANNER, VERSION

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VERSION)
def cli():
    """ProxyPool validator cli (subset)"""


@cli.command(name="once")
def once():
    """ Un solo ciclo de fetch+check y termina """
    click.echo(BANNER)
    startOnce()


@cli.command(name="fetcher")
def fetcher():
    """ Ver fuentes activas """
    from helper.fetch import _discover_fetchers
    from handler.configHandler import ConfigHandler
    conf = ConfigHandler()
    exclude = conf.fetcherExclude
    fetcher_classes = _discover_fetchers(exclude)
    click.echo("Active fetchers (%d):" % len(fetcher_classes))
    for cls in fetcher_classes:
        click.echo("  - %s" % cls.name)
    if exclude:
        click.echo("\nExcluded: %s" % ", ".join(exclude))


if __name__ == '__main__':
    cli()
