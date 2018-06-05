radon 分布式数据库测试
=======

[radon](https://github.com/radondb/radon) 文档都在 docs 文件夹

测试环境
* macos
* docker 
* docker-compose

安装在宿主机的
* radon [安装文档](https://github.com/radondb/radon/blob/master/docs/how_to_build_and_run_radon.md) 3306, 8080 
* mysql-client v5.6


测试的部署结构 (mysql其实是5.7.20版的)
```
radon(宿主) ---> backend mysql1 (docker)
           ---> backend mysql2 (docker)
           ---> backend mysql3 (docker)
```


按照文档编译和启动好 radon
```
bin/radon -c bin/radon.default.json
```

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
或者在 radon目录 `cat bin/radon-meta/backend.json` 也能看到上面的结果

删除backend
```
curl -X DELETE http://127.0.0.1:8080/v1/radon/backend/mysql2
```

看起来简单的环境搭建好了，那么怎么测试呢？

连接 radon
```
$ mysql -uroot -h127.0.0.1 -P3306
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 2
Server version: 5.7-Radon-1.0
....
```

```
mysql> CREATE DATABASE SBTEST;
Query OK, 3 rows affected (0.06 sec)

mysql> use sbtest;

Database changed

mysql> CREATE TABLE t1(id int, age int) PARTITION BY HASH(id);
Query OK, 0 rows affected (0.36 sec)

mysql> SHOW CREATE TABLE t1\G;
*************************** 1. row ***************************
       Table: t1
Create Table: CREATE TABLE `t1` (
  `id` int(11) DEFAULT NULL,
  `age` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1
1 row in set (0.02 sec)

ERROR:
No query specified
mysql> INSERT INTO t1(id, age) values(1, 25);
Query OK, 1 row affected (0.02 sec)

mysql> INSERT INTO t1(id, age) values(3, 22);
Query OK, 1 row affected (0.01 sec)

mysql> INSERT INTO t1(id, age) values(12, 22);
Query OK, 1 row affected (0.02 sec)

mysql> INSERT INTO t1(id, age) values(13, 22);
Query OK, 1 row affected (0.00 sec)

mysql> INSERT INTO t1(id, age) values(33, 22);
Query OK, 1 row affected (0.00 sec)

mysql> select *from t1;
+------+------+
| id   | age  |
+------+------+
|    3 |   22 |
|   12 |   22 |
|    1 |   25 |
|   13 |   22 |
|   33 |   22 |
+------+------+
5 rows in set (0.07 sec)
```

这时候去看看backend 发生了什么
```
$ docker exec -it mysql2 bash
root@ddd50b802e35:/# mysql -p
..

mysql> select TABLE_NAME, TABLE_ROWS from information_schema.TABLES where table_schema='sbtest';
+------------+------------+
| TABLE_NAME | TABLE_ROWS |
+------------+------------+
| t1_0010    |          0 |
| t1_0011    |          1 |
| t1_0012    |          0 |
| t1_0013    |          0 |
| t1_0014    |          0 |
| t1_0015    |          0 |
| t1_0016    |          0 |
| t1_0017    |          1 |
| t1_0018    |          0 |
| t1_0019    |          0 |
+------------+------------+
10 rows in set (0.00 sec)

mysql> select *from t1_0011;
+------+------+
| id   | age  |
+------+------+
|    3 |   22 |
+------+------+
1 row in set (0.00 sec)
```

测到这里应该是可用，对于场景和压测还需要进一步研究。