#!/usr/bin/env python
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from time import sleep, time


CLIENT_DSN = "host='localhost' port=5432 user=postgres dbname=client"
SERVER_DSN = "host='localhost' port=5432 user=postgres dbname=server"


def get_client_count():
    client.execute("SELECT count(1) FROM presentation_consumer_table;")
    value = client.fetchone()
    return value[0]


def get_server_count():
    server.execute("SELECT count(1) FROM presentation_example;")
    value = server.fetchone()
    return value[0]


if __name__ == '__main__':

    c_pgsql = connect(CLIENT_DSN)
    c_pgsql.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    client = c_pgsql.cursor()
    
    s_pgsql = connect(SERVER_DSN)
    s_pgsql.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    server = s_pgsql.cursor()
    

    while True:
    
        client_count = get_client_count()
        server_count = get_server_count()
        
        print '%i: Server: %s Client: %i' % (time(), 
                                              server_count,
                                              client_count)
        sleep(1)