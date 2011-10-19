On Rabbits and Elephants for pgConf.eu 2011
===========================================

Installation
------------

1. Install RabbitMQ and Management Plugin from:

     http://www.rabbitmq.com

2. Install pgbench from contrib

4. Install the pg_amqp extension

    easy_install pgxnclient
    pgxnclient install pg_amqp

5. Run setup-full.sh to do both a server a client

   or

   Run setup-client.sh to do only a client

Use
---

Kick off all three apps in different terminals:

1. Kick off ./consumer.py

2. Kick off ./watch-db-full.py or ./watch-db-client.py

3. Kick off ./watch-messages.py

Version Information
-------------------
This was developed, tested and demoed on Mac OSX 10.7.2 with PostgreSQL 9.1rc1
and RabbitMQ 2.6.1 using Python v2.7.1 and Pika 0.9.5. Your mileage may vary.
