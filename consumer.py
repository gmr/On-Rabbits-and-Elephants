#!/usr/bin/env python
from pika import SelectConnection, ConnectionParameters
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from json import loads
import sys

DSN = "host='localhost' port=5432 dbname=pgbench_client"
queues = ['accounts', 'branches', 'history', 'tellers']

class TriggerConsumer(object):

    def __init__(self):
        self.pgsql = connect(DSN)
        self.pgsql.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.pgsql.cursor()

    def _on_connected(self, connection):
        self.connection = connection
        self.connection.channel(self._on_channel_open)
        self.connection.channel(self._on_channel_open)
        self.connection.channel(self._on_channel_open)
        self.connection.channel(self._on_channel_open)

    def _on_channel_open(self, channel):
        queue_name = queues.pop()
        print "Channel %i opening, subscribing to %s" % \
                (channel.channel_number, queue_name)
        channel.basic_consume(self._handle_delivery, queue=queue_name)

    def _handle_delivery(self, channel, method_frame, header_frame, body):

        # Update the data
        message = loads(body)

        parameters = dict()

        if message['event'] == 'INSERT':
            fields = list()
            for field in message['new']:
                fields.append(field)
            values = list()
            for field in fields:
                values.append('%%(%s)s' % field)
            sql = 'INSERT INTO %s (%s) VALUES (%s)' % (method_frame.routing_key, ', '.join(fields), ', '.join(values))
            self.cursor.execute(sql, message['new'])

        elif message['event'] == 'UPDATE':
            sql = ['UPDATE %s SET ' % method_frame.routing_key]
            for field in message['new']:
                parameters['new_%s' % field] = message['new'][field]
                sql.append('%s = %%(new_%s)s' % (field, field))
                sql.append(',')
            sql.pop(len(sql) - 1)
            sql.append(' WHERE ')
            for field in message['old']:
                parameters['old_%s' % field] = message['old'][field]
                sql.append('%s = %%(old_%s)s' % (field, field))
                sql.append(' AND ')
            sql.pop(len(sql) - 1)
            self.cursor.execute(''.join(sql), parameters)

        elif message['event'] == 'DELETE':
            fields = list()
            for field in message['old']:
                fields.append('%s = %%(%s)s' % (field, field))
            sql = 'DELETE FROM %s WHERE %s' % (method_frame.routing_key, ', '.join(fields))
            self.cursor.execute(sql, message['old'])

        # Ack the message
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)


if __name__ == '__main__':

    consumer = TriggerConsumer()

    # Connect to RabbitMQ
    host = (len(sys.argv) > 1) and sys.argv[1] or '127.0.0.1'
    connection = SelectConnection(ConnectionParameters(host),
                                  consumer._on_connected)
    # Loop until CTRL-C
    try:
        print "Starting IOLoop"
        # Start our blocking loop
        connection.ioloop.start()

    except KeyboardInterrupt:

        # Close the connection
        connection.close()

        # Loop until the connection is closed
        connection.ioloop.start()
