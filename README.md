# sbds
Steem Block Data Service

##Install
```pip3 install -e git+git@github.com:steemit/sbds.git#egg=sbds```

##Use
+  *sbds*: `sbds` or `sbds --help`
+  *notify*: `wsdump.py --text '{"jsonrpc": "2.0", "method": "call", "params": ["database_api","set_block_applied_callback",[1234]], "id": 1}' --raw
wss://steemit.com/wspa | notify`
