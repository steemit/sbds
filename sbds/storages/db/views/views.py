# -*- coding: utf-8 -*-

from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import table
from sqlalchemy.ext import compiler


class CreateView(DDLElement):
    def __init__(self, name, sql_text):
        self.name = name
        self.sql_text = sql_text

class DropView(DDLElement):
    def __init__(self, name):
        self.name = name

@compiler.compiles(CreateView)
def compile(element, compiler, **kw):
    return element.sql_text

@compiler.compiles(DropView)
def compile(element, compiler, **kw):
    return "DROP VIEW %s" % (element.name)

def view(name, metadata, sql_text):
    t = table(name)
    CreateView(name, sql_text).execute_at('after-create', metadata)
    DropView(name).execute_at('before-drop', metadata)
    return t
