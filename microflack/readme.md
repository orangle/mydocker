通过etcd来动态调整haproxy的配置

查看haproxy

```
http://127.0.0.1/stats
```

增加一个backend
```
export ETCD=http://192.168.1.30:2379
curl -X PUT "$ETCD/v2/keys/services/monolith/location" -d value="/api"
curl -X PUT "$ETCD/v2/keys/services/monolith/upstream/server" -d value="192.168.1.30:5000"

curl -X DELETE "$ETCD/v2/keys/services/monolith?recursive=true"
```