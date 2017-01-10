# sbds
Steem Block Data Service

## Install
```pip3 install -e git+git@github.com:steemit/sbds.git#egg=sbds```

## Use
### Individual Commands
**sbds**: `sbds` or `sbds --help`

**notify**: `wsdump.py --text '{"jsonrpc": "2.0", "method": "call", "params": ["database_api","set_block_applied_callback",[1234]], "id": 1}' --raw
wss://steemit.com/wspa | notify`

**s3**: `s3 create-bucket <bucket name>` or `sbds --start 1 | s3
   put-json-blocks <bucket-name> -`

**db**: `sbds | db insert-blocks` or `db --help`


### Docker
#### Build
`docker build --name sbds-image .`

#### Block Streaming To DB


```
docker run --rm \
    --env 'DATABASE_URL=sqlite:///local.db' \
    --env 'WEBSOCKET_URL=wss://steemit.com/wspa' \
    --name sbds-blocks \
    sbds-image sbds-populate.sh

```


#### HTTP Server
```
docker run --rm \
    --env 'DATABASE_URL=sqlite:///local.db' \
    --env 'WEBSOCKET_URL=wss://steemit.com/wspa' \
    --publish 127.0.0.1:8080:8080 \
    --name sbds-web \
    sbds-image dev-server 
```

