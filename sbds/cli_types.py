# -*- coding: utf-8 -*-
import click
from furl import furl

SCHEMES = (
    'file',
    's3',
    'postgres',
    'postgres+psycopg2',
    'https'
)


class URIParamType(click.ParamType):
    name = 'uri'

    def convert(self, value, param, ctx):
        try:
            if not isinstance(value, furl.furl.furl):
                uri = furl(value)
            if uri.scheme not in SCHEMES:
                self.fail(f'{uri.scheme} is not a supported scheme')
            if uri.path.isabsolute:
                self.fail(f'{uri.path} is a relative path, uri must be absolute path')
        except ValueError:
            self.fail('%s is not a valid uri' % value, param, ctx)


URI = URIParamType()
