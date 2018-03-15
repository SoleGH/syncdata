
#### 主数据库配置  begin ###############################
1.修改配置文件，命令：vim /etc/my.cnf 或 、/etc/mysql/my.cnf，
在mysql配置下添加下列代码：
    [mysqld]
    datadir=/var/lib/mysql
    socket=/var/lib/mysql/mysql.sock

    `# 新添加的部分
    # 配置主从时需要添加以下信息 start
    innodb_file_per_table=NO
    log-bin=/var/lib/mysql/master-bin #log-bin没指定存储目录，则是默认datadir指向的目录
    binlog_format=mixed
    server-id=200 
    #每个服务器都需要添加server_id配置，各个服务器的server_id需要保证唯一性，实践中通常设置为服务器IP地址的最后一位
    #配置主从时需要添加以下信息 end 

2.重启mariadb服务，输入命令：
  [root@localhost ~]# systemctl restart mariadb.service

3.登录mariadb  [root@localhost ~]# mysql -u root -padmin  注：-p后是密码，中间没有空格 

4.创建帐号并赋予replication的权限  从库,从主库复制数据时需要使用这个帐号进行：
    MariaDB [(none)]> GRANT REPLICATION SLAVE ON *.* TO 'root'@'10.69.5.%' IDENTIFIED BY 'kitoadmin';
    返回信息如下：Query OK, 0 rows affected (0.00 sec)

5.备份数据库数据，用于导入到从数据库中

    5.1 加锁 备份的时候是不让往库中写数据的，所以数据库要加锁，只能读
        MariaDB [(none)]> FLUSH TABLES WITH READ LOCK;
        返回消息如下：Query OK, 0 rows affected (0.00 sec)
    5.2 查看主库log文件：
        MariaDB [(none)]> SHOW MASTER STATUS;
        返回信息：
        +------------------+----------+--------------+------------------+
        | File             | Position | Binlog_Do_DB | Binlog_Ignore_DB |
        +------------------+----------+--------------+------------------+
        | mysql-bin.000001 |      694 |              |                  |
        +------------------+----------+--------------+------------------+
        记录File 和 Position（配置从服务器会用到）
    5.3 备份数据将主数据库数据备份到/root/db.sql：
        [root@localhost ~]# mysqldump -uroot -p --all-databases > /root/db.sql
    5.4 解锁
        MariaDB [(none)]> UNLOCK TABLES;
        返回信息：
        Query OK, 0 rows affected (0.00 sec)

#### 主数据库配置  end ###############################


#### 从数据库配置  begin ###############################
1.导入主库的数据（db.sql从主服务器copy）：
    [root@localhost ~]# mysql -uroot -p < db.sql

2.从服务器/etc/my.cnf配置,设置relay-log  my.cnf文件中添加一行relay_log=relay-bin  如果不设置，默认是按主机名 + “-relay-bin”生成relay log。
    [mysqld]
    datadir=/var/lib/mysql
    socket=/var/lib/mysql/mysql.sock
    # Disabling symbolic-links is recommended to prevent assorted security risks
    symbolic-links=0

    #配置主从时需要添加以下信息 start
    innodb_file_per_table=NO
    server-id=201 #一般与服务器ip的最后数字一致
    relay-log=/var/lib/mysql/relay-bin
    #配置主从时需要添加以下信息 end 

3.重启服务:
    [root@localhost ~]# systemctl restart mariadb.service

4.登录mariadb,配置从服务器：
    [root@localhost ~]# mysql -u root -padmin
    MariaDB [(none)]> CHANGE MASTER TO MASTER_HOST='10.8.0.5',MASTER_USER='root', MASTER_PASSWORD='kitoadmin', MASTER_LOG_FILE='youself master-bin.000001', MASTER_LOG_POS= youself 694;
    返回信息：
    Query OK, 0 rows affected (0.02 sec)

5.开启主从复制
    MariaDB [(none)]> START SLAVE;
    Query OK, 0 rows affected (0.00 sec)

6.查看从库状态
    MariaDB [(none)]> show slave status\G
    返回信息：
        *************************** 1. row ***************************
                        Slave_IO_State: Waiting for master to send event
                            Master_Host: 10.69.5.200
                            Master_User: root
                            Master_Port: 3306
                            Connect_Retry: 60
                        Master_Log_File: master-bin.000001
                    Read_Master_Log_Pos: 694
                        Relay_Log_File: relay-bin.000003
                            Relay_Log_Pos: 530
                    Relay_Master_Log_File: master-bin.000001
                        Slave_IO_Running: Yes
                        Slave_SQL_Running: Yes
                        Replicate_Do_DB: 
                    Replicate_Ignore_DB: 
                    Replicate_Do_Table: 
                Replicate_Ignore_Table: 
                Replicate_Wild_Do_Table: 
            Replicate_Wild_Ignore_Table: 
                            Last_Errno: 0
                            Last_Error: 
                            Skip_Counter: 0
                    Exec_Master_Log_Pos: 694
                        Relay_Log_Space: 818
                        Until_Condition: None
                        Until_Log_File: 
                            Until_Log_Pos: 0
                    Master_SSL_Allowed: No
                    Master_SSL_CA_File: 
                    Master_SSL_CA_Path: 
                        Master_SSL_Cert: 
                        Master_SSL_Cipher: 
                        Master_SSL_Key: 
                    Seconds_Behind_Master: 0
            Master_SSL_Verify_Server_Cert: No
                            Last_IO_Errno: 0
                            Last_IO_Error: 
                        Last_SQL_Errno: 0
                        Last_SQL_Error: 
            Replicate_Ignore_Server_Ids: 
                        Master_Server_Id: 200
            1 row in set (0.00 sec)
    注意：结果中Slave_IO_Running和Slave_SQL_Running必须为Yes，如果不是，需要根据提示的错误修改。
#### 从数据库配置  end ###############################