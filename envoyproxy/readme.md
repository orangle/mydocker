
#### simple install 
```
docker pull envoyproxy/envoy:latest

docker run --rm -p 10000:10000 -p 9901:9901 \
        -v `pwd`/baidu_com_proxy.v2.yaml:/etc/envoy/envoy.yaml  envoyproxy/envoy:latest

curl -v localhost:10000
```

#### lb testing

* client (localhost) 
* envoy (docker)
* two backend (192.168.1.30)

```
client --> envoy --> s1 (10001) 
                 --> s2 (10002)
```


```
$ python app.py --port 10003 --hello 10003
$ python app.py --port 10002 --hello 10002

$ curl 127.0.0.1:10003
10003%

$ curl 127.0.0.1:10002
10002%

docker run --rm -p 10000:10000 -p 9901:9901 \
        -v `pwd`/base_conf.yaml:/etc/envoy/envoy.yaml  envoyproxy/envoy:latest

$ curl 127.0.0.1:10000 -i
```

`lb_policy: ROUND_ROBIN` 的时候，如果一个backend down了，那么会有一半的请求挂掉。
`lb_policy: LEAST_REQUEST` 也无法做到单台的故障转移

#### nginx upstream

跟上面的结构一样，测试下nginx的故障转移, 假设本地安装了nginx

```
$ python app.py --port 10003 --hello 10003
$ python app.py --port 10002 --hello 10002

$ curl 127.0.0.1:10003
10003%

$ curl 127.0.0.1:10002
10002%

$ nginx -v
nginx version: openresty/1.13.6.1

$ nginx -c `pwd`/nginx.conf -p `pwd` -t

$ curl 127.0.0.1:10000 -i
```

简单配置的情况下就可以做到故障转移，backend只要不全部down，整体还可以对外服务，可用性相对好说好一点