# -*- coding: utf-8 -*-

ARRAY_DISTINCT = '''
CREATE OR REPLACE FUNCTION array_distinct(anyarray)
RETURNS anyarray AS $$
  SELECT ARRAY(SELECT DISTINCT unnest($1))
$$ LANGUAGE sql;
'''

ARRAY_APPEND_DISTINCT = '''
CREATE OR REPLACE FUNCTION array_append_distinct(anyarray, anyelement)
RETURNS anyarray AS $$
  SELECT ARRAY(SELECT unnest($1) union SELECT $2)
$$ LANGUAGE sql;
'''
