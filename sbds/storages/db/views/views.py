# -*- coding: utf-8 -*-

from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import table
from sqlalchemy.ext import compiler
from sqlalchemy import event
from sqlalchemy import DDL


class CreateView(DDLElement):
    def __init__(self, name, sql_text):
        self.name = name
        self.sql_text = sql_text


class DropView(DDLElement):
    def __init__(self, name):
        self.name = name


@compiler.compiles(CreateView)
def compile(element, compiler, **kw):
    return f'CREATE OR REPLACE VIEW {element.name} AS {element.sql_text}'


@compiler.compiles(DropView)
def compile(element, compiler, **kw):
    return f'DROP VIEW IF EXISTS {element.name}'


def view(name, metadata, sql_text):
    t = table(name)
    CreateView(name, sql_text).execute_at('after-create', metadata)
    DropView(name).execute_at('after-drop', metadata)
    return t
