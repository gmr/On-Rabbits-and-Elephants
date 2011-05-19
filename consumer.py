#!/usr/bin/env python
from pika import SelectConnection, ConnectionParameters
from optparse import OptionParser
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from json import loads
import sys


DSN = "host='localhost' port=5432 user=postgres dbname=client"

INSERT_QUERY = """
    INSERT INTO presentation_consumer_table
        (row_id, occurred_at, payload)
        VALUES
        (%(row_id)s, %(occurred_at)s, %(payload)s);"""

DELETE_QUERY = """
    DELETE FROM presentation_consumer_table
        WHERE row_id = %(row_id)s;"""

UPDATE_QUERY = """
    UPDATE presentation_consumer_table
        SET
            changed_at = CURRENT_TIMESTAMP,
            row_id = %(row_id)s,
            occurred_at = %(occurred_at)s,
            payload = %(payload)s
        WHERE row_id = %(old_row_id)s;"""


class ExampleConsumer(object):

    def __init__(self):
        self.pgsql = connect(DSN)
        self.pgsql.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.pgsql.cursor()

    def _on_connected(self, connection):
        self.connection = connection
        self.connection.channel(self._on_channel_open)

    def _on_channel_open(self, channel):
        self.channel = channel
        self.channel.basic_consume(self._handle_delivery, queue='transactions')

    def _handle_delivery(self, channel, method_frame, header_frame, body):

        # Update the data
        message = loads(body)

        # Insert the data
        if message['operation'] == 'insert':
            data = {'row_id': message['data']['row_id'],
                    'occurred_at': message['data']['occurred_at'],
                    'payload': message['data']['payload']}
            self.cursor.execute(INSERT_QUERY, data)

        # Update the data
        elif message['operation'] == 'update':
            data = {'row_id': message['new']['row_id'],
                    'occurred_at': message['new']['occurred_at'],
                    'payload': message['new']['payload'],
                    'old_row_id': message['old']['row_id']}
            self.cursor.execute(UPDATE_QUERY, data)

        # Delete the row
        elif message['operation'] == 'delete':
            data = {'row_id': message['data']['row_id']}
            self.cursor.execute(DELETE_QUERY, data)

        # Ack the message
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)


if __name__ == '__main__':

    consumer = ExampleConsumer()

    # Connect to RabbitMQ
    host = (len(sys.argv) > 1) and sys.argv[1] or '127.0.0.1'
    connection = SelectConnection(ConnectionParameters(host),
                                  consumer._on_connected)
    # Loop until CTRL-C
    try:
        # Start our blocking loop
        connection.ioloop.start()

    except KeyboardInterrupt:

        # Close the connection
        connection.close()

        # Loop until the conneciton is closed
        connection.ioloop.start()
