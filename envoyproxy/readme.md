
```
docker pull envoyproxy/envoy:latest

docker run --rm -p 10000:10000 -p 9901:9901 \
        -v `pwd`/baidu_com_proxy.v2.yaml:/etc/envoy/envoy.yaml  envoyproxy/envoy:latest

curl -v localhost:10000
```

