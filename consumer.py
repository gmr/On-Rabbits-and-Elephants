#!/usr/bin/env python
from pika import SelectConnection, ConnectionParameters
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from json import loads
import os
import sys

DSN = "host='localhost' port=5432 dbname=pgbench_client"
queues = ['accounts', 'branches', 'history', 'tellers']

class TriggerConsumer(object):

    def __init__(self):
        self.pgsql = connect(DSN)
        self.pgsql.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.pgsql.cursor()
        self._queues = dict()
        self._channels = dict()

    def _on_connected(self, connection):
        self.connection = connection
        self.connection.channel(self._on_channel_open)
        self.connection.channel(self._on_channel_open)
        self.connection.channel(self._on_channel_open)
        self.connection.channel(self._on_channel_open)

    def _on_channel_open(self, channel):
        self._queues[channel.channel_number] = '%s:%s' % (queues.pop(),
                                                          os.uname()[1])
        self._channels[channel.channel_number] = channel
        print "Channel %i opening, declaring %s" % \
                (channel.channel_number,
                 self._queues[channel.channel_number])

        channel.queue_declare(queue=self._queues[channel.channel_number],
                              auto_delete=True,
                              callback=self._on_queue_declared)


    def _on_queue_declared(self, frame):
        table = self._queues[frame.channel_number].split(':')
        print "%s declared, binding" % self._queues[frame.channel_number]
        self._channels[frame.channel_number].queue_bind(exchange="pgConf",
                                 queue=self._queues[frame.channel_number],
                                 routing_key="public.pgbench_%s" % table[0],
                                 callback=self._on_queue_bound)

    def _on_queue_bound(self, frame):
        print "%s bound, subscribing" % self._queues[frame.channel_number]
        self._channels[frame.channel_number].basic_consume(self._handle_delivery,
                                   queue=self._queues[frame.channel_number],
                                   no_ack=True)

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
