#!/usr/bin/env python

import click

from main.config import config
from main.libtaiga import authenticate


@click.command()
@click.option('--u', 'username', default="admin", type=str)
@click.option('--p', 'password', default="123123", type=str)
# def main(username, password):
def main(*args, **kw):
    result = authenticate(config.auth_url, kw['username'], kw['password'])
    print("result = ", result)
    return result


if __name__ == '__main__':
    main()
