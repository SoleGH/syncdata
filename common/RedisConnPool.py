# coding:utf-8

import redis

class Rcon(object):
    """
    管理connect 和 pool
    """
    pools = {}
    rcons = {}
    @staticmethod
    def get_conn(db_num=0):
        if db_num not in Rcon.rcons.keys():
            if db_num not in Rcon.pools.keys():
                Rcon.pools[db_num] = redis.ConnectionPool(host="10.9.40.114", port=6379, password="admin",
                                                      db=db_num)
                Rcon.rcons[db_num] = redis.Redis(connection_pool=Rcon.pools[db_num])
                return Rcon.rcons[db_num]
            else:
                Rcon.rcons[db_num] = redis.Redis(connection_pool=Rcon.pools[db_num])
                return Rcon.rcons[db_num]
        else:
            return Rcon.rcons[db_num]
        
        
if __name__ == "__main__":
	conn = Rcon.get_conn(0)
	print conn.sinter("factory_id") 
