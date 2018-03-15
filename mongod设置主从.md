### 1.启动主数据库命令
    
    $mongod --config /etc/mongod.conf.orig --master
### 2.启动从数据库
    $mongod --config /etc/mongod.conf.orig --slave --autoresync --slavedelay=10 --source master-ip:master-port

```
sudo docker run -d -v /var/lib/mongo3:/data/db -v /home/user/mongo-master.conf:/etc/mongod.conf.orig -p 27020:27017 mongo
```


### master参数配置
```
[root@mongodb1 log]# cat /etc/mongod.conf
port=27017
dbpath=/data/db
logpath=/data/log/mongod.log
fork = true
master=true
oplogSize=2048
```
### slave配置
```
[root@mongodb2 ~]# cat /etc/mongod.conf
port=27017
dbpath=/data/db
logpath=/data/log/mongod.log
fork = true
slave = true
source = 192.168.56.80:27017
```


### master端查看主从配置
```
rs.printReplicationInfo();
```
### slave端查看主从配置
```
rs.printSlaveReplicationInfo();
```
```
mkdir -p /data/{mongodb27017,mongodb27018}
#master:
/usr/local/mongodb/bin/mongod --master --port 27017 --dbpath=/data/mongodb27017/ --logpath /data/mongodb27017/mongodb.log &
#slave:
/usr/local/mongodb/bin/mongod --slave --source 10.10.10.56:27017 --port 27018 --dbpath=/data/mongodb27018/ --logpath /data/mongodb27018/mongodb.log &
```