On Rabbits and Elephants
========================

Installation
------------

1. Install RabbitMQ and Management Plugin from:

 http://www.rabbitmq.com 

2. In the RabbitMQ Management Web UI add:

 1. A direct exchange called "postgres"
 
 2. A queue called "transactions"

 3. Bind the queue "transactions" to the exchange "postgres" with the routing key "pubish_transactions"

3. Create two databases:

 1. createdb server
 
 2. createdb client
 
4. Install pg_amqp in to the "server" database. PostgreSQL from:

 https://labs.omniti.com/labs/pgtreats/browser/trunk/contrib/pg_amqp 

 or
   
 > easy_install pgxnclient
 > pgxnclient install pg_amqp
 
 then
   
 > psql server < pg_amqp.sql

5. Import the schemas

 > psql server < server.sql
 > psql client < client.sql

6. Do some test events and see if they end up in the "postgres" queue in the RabbitMQ Management Web UI

 > INSERT INTO presentation_example (payload) values ( 'this is a test') RETURNING row_id;
 > UPDATE presentation_example SET payload = 'Updated test message' WHERE row_id = 1;
 > DELETE FROM presentation_example WHERE row_id = 1;

7. Install client.sql in another database and keep track of connection info.

8. Install pika, the Python RabbitMQ client library:

 > easy_install pika

Use
---

Kick off all three apps in different terminals:

1. Kick off ./consumer.py

2. Kick off ./watcher.py 

3. Kick off ./producer.py

Notes
-----

I included a setup.sh file here if install the requirements, it will do all of the postgres specific schema setup and the pg_amqp.sql file included in the distro is copied from my contrib install of pg_amqp and your milage may vary.

I used PostgreSQL 9.0.3, RabbitMQ 2.4.1, pika 0.9.6pre0 (github master), psycopg2 2.4.1 and Python 2.6.1