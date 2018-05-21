#!/usr/bin/env python

import click

from libconfig import setup
from libconfig import authenticate


@click.command()
@click.option('--u', 'username', default="admin", type=str)
@click.option('--p', 'password', default="1231234", type=str)
# def main(username, password):
def main(*args, **kw):
    config = setup()
    token = authenticate(config.auth_url, kw['username'], kw['password'])
    if isinstance(token, str):
        result = token
    else:
        result = token['_error_message']
    print("result = ", result)
    return result


if __name__ == '__main__':
    main()
