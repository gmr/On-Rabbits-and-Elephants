#!/usr/bin/env python
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from random import randint
from time import time
from uuid import uuid4

DSN = "host='localhost' port=5432 user=postgres dbname=server"


#cursor = None
delete_list = set()

INSERT_QUERY = """
    INSERT INTO presentation_example 
        (payload) VALUES (%(payload)s);"""
        
DELETE_QUERY = """
    DELETE FROM presentation_example WHERE row_id = %(row_id)s
    """

UPDATE_QUERY = """
    UPDATE presentation_example 
        SET
            occurred_at = CURRENT_TIMESTAMP,
            payload = %(payload)s
        WHERE
            row_id = %(row_id)s
    """

def random_text():
    return str(uuid4())

def insert():
    cursor.execute(INSERT_QUERY, {'payload': random_text()})
    
def update(max_id):
    id_to_update = randint(1, max_id)
    if id_to_update in delete_list:
        return
    cursor.execute(UPDATE_QUERY, {'row_id': id_to_update,
                                  'payload': random_text()})
    
def delete(max_id):

    id_to_delete = randint(1, max_id)
    if id_to_delete in delete_list:
        return
        
    delete_list.add(id_to_delete)
    cursor.execute(DELETE_QUERY, {'row_id': id_to_delete})


if __name__ == '__main__':
    pgsql = connect(DSN)
    pgsql.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = pgsql.cursor()

    for iteration in xrange(1,10000000):
        choice = randint(0,100)
        if choice < 5:
            delete(iteration)
        elif choice >= 5 and choice < 25:
            update(iteration)
        elif choice >= 25:
            insert()