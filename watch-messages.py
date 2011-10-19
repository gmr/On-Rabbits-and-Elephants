#!/usr/bin/env python
from pika import SelectConnection, ConnectionParameters
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from json import loads
import sys


class TriggerConsumer(object):

    def __init__(self):
        self._messages = 0
        self._deletes = 0
        self._inserts = 0
        self._updates = 0

    def _on_connected(self, connection):
        self.connection = connection
        self.connection.channel(self._on_channel_open)


    def _on_channel_open(self, channel):
        queue_name = 'watch'
        print "Channel %i opened, subscribing to %s" % \
              (channel.channel_number, queue_name)
        channel.basic_consume(self._handle_delivery, queue=queue_name,
                              no_ack=True)

    def _handle_delivery(self, channel, method_frame, header_frame, body):

        # Update the data
        message = loads(body)
        self._messages += 1

        if message['event'] == 'INSERT':
            self._inserts += 1

        elif message['event'] == 'UPDATE':
            self._updates += 1

        elif message['event'] == 'DELETE':
            self._deletes = 0

        if self._messages % 1000 == 0:
            print '%i Messages, %i Inserts, %i Updates, %i Deletes' % \
                  (self._messages, self._inserts, self._updates, self._deletes)


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
