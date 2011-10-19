#!/usr/bin/env python
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from time import sleep

CLIENT_DSN = "host='localhost' port=5432 dbname=pgbench_client"
SERVER_DSN = "host='localhost' port=5432 dbname=pgbench_server"


def get_row_count(cursor, table):
    cursor.execute("SELECT count(1) FROM %s;" % table)
    value = cursor.fetchone()
    return value[0]


if __name__ == '__main__':

    c_pgsql = connect(CLIENT_DSN)
    c_pgsql.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    client = c_pgsql.cursor()

    s_pgsql = connect(SERVER_DSN)
    s_pgsql.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    server = s_pgsql.cursor()


    while True:

        print 'Server: '
        print 'public.pgbench_accounts: %i' % \
              get_row_count(server, 'public.pgbench_accounts')
        print 'public.pgbench_branches: %i' % \
              get_row_count(server, 'public.pgbench_branches')
        print 'public.pgbench_history: %i' % \
              get_row_count(server, 'public.pgbench_history')
        print 'public.pgbench_tellers: %i' % \
              get_row_count(server, 'public.pgbench_tellers')
        print
        print 'Client: '
        print 'public.pgbench_accounts: %i' % \
              get_row_count(client, 'public.pgbench_accounts')
        print 'public.pgbench_branches: %i' % \
              get_row_count(client, 'public.pgbench_branches')
        print 'public.pgbench_history: %i' % \
              get_row_count(client, 'public.pgbench_history')
        print 'public.pgbench_tellers: %i' % \
              get_row_count(client, 'public.pgbench_tellers')
        print

        sleep(5)
