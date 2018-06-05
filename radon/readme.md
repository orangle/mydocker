radon 分布式数据库测试
=======

测试环境
* macos
* docker 
* docker-compose

安装在宿主机的
* radon [安装文档](https://github.com/radondb/radon/blob/master/docs/how_to_build_and_run_radon.md) 3306, 8080 
* mysql-client v5.6

docker 启动mysql集群用来测试

```
$ mkdir mysql1
$ mkdir mysql2
$ mkdir mysql3
```

启动docker集群
```
$ docker-compose up -d
$ docker-compose ps
 Name              Command             State           Ports
---------------------------------------------------------------------
mysql1   docker-entrypoint.sh mysqld   Up      0.0.0.0:3307->3306/tcp
mysql2   docker-entrypoint.sh mysqld   Up      0.0.0.0:3308->3306/tcp
mysql3   docker-entrypoint.sh mysqld   Up      0.0.0.0:3309->3306/tcp
```

进入某个容器看看好用吗
```
$ docker exec -it mysql3 bash
root@7c16a446d174:/# mysql -p
Enter password:
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 17
Server version: 5.7.20 MySQL Community Server (GPL)
...
```


添加backend
```
curl -i -H 'Content-Type: application/json' -X POST -d \
    '{"name": "mysql1", "address": "127.0.0.1:3307", "user":"root", "password": "root", "max-connections":1024}'\
    http://127.0.0.1:8080/v1/radon/backend

curl -i -H 'Content-Type: application/json' -X POST -d \
    '{"name": "mysql2", "address": "127.0.0.1:3308", "user":"root", "password": "root", "max-connections":1024}'\
    http://127.0.0.1:8080/v1/radon/backend

curl -i -H 'Content-Type: application/json' -X POST -d \
    '{"name": "mysql3", "address": "127.0.0.1:3309", "user":"root", "password": "root", "max-connections":1024}'\
    http://127.0.0.1:8080/v1/radon/backend
```

查看backend
```
$ curl http://127.0.0.1:8080/v1/debug/backendz | python -m json.tool
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   394  100   394    0     0   102k      0 --:--:-- --:--:-- --:--:--  128k
[
    {
        "name": "mysql1",
        "address": "127.0.0.1:3307",
        "user": "root",
        "password": "root",
        "database": "",
        "charset": "utf8",
        "max-connections": 1024
    },
    {
        "name": "mysql2",
        "address": "127.0.0.1:3308",
        "user": "root",
        "password": "root",
        "database": "",
        "charset": "utf8",
        "max-connections": 1024
    },
    {
        "name": "mysql3",
        "address": "127.0.0.1:3309",
        "user": "root",
        "password": "root",
        "database": "",
        "charset": "utf8",
        "max-connections": 1024
    }
]
```

删除backend
```
curl -X DELETE http://127.0.0.1:8080/v1/radon/backend/mysql2
```