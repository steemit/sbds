# coding=utf-8

from sqlalchemy import Integer
from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import DateTime
from sqlalchemy import String

uint16_t = Integer()
uint32_t = Integer()
uint64_t = Integer()
int16_t =  Integer()

account_name_type =  Unicode(50)
asset = Numeric(15, 6)
permalink = Unicode(512)
time_point_sec = DateTime()
public_key_type = String(100)


schema = {
"account_name_type": {
    "type": "string",
    "minLength": 3,
    "maxLength": 16,
    "description": "https://github.com/steemit/steem/blob/master/libraries/protocol/include/steemit/protocol/config.hpp#L207"
  },
  "time_point_sec": {
    "type": "string",
    "format": "date-time"
  },
  "asset": {
    "type": "string",
    "pattern": "\\d+(\\.\\d+)?\\s+(STEEM|SBD|VESTS)+"
  },
  "public_key_type": {
    "type": "string",
    "minLength": 10,
    "maxLength": 100
  },
  "block_id_type": {
    "$ref": "#/definitions/uint32_t"
  },
"signed_block_header": {
    "type": "string"
},
"uint16_t": {
    "type": "integer",
    "min":  0,
    "max":  65535
},
"uint32_t": {
    "type": "integer",
    "min":  0,
    "max":  4294967295
},
"uint64_t": {
    "type": "integer",
    "min":  0
},
"int16_t": {
    "type": "integer",
    "min":  32768,
    "max":  32767
}
}
