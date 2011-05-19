On Rabbits and Elephants
========================

Installation
------------

1. Install RabbitMQ and Management Plugin from:

   http://www.rabbitmq.com 

2. Install pg_amqp in PostgreSQL from:

   https://labs.omniti.com/labs/pgtreats/browser/trunk/contrib/pg_amqp 

3. In the RabbitMQ Management Web UI add:

 1. A direct exchange called "postgres"
 
 2. A queue called "transactions"

 3. Bind the queue "transactions" to the exchange "postgres" with the routing key "pubish_transactions"

4. Modify and then import the server.sql into your primary database

5. Do some test events and see if they end up in the postgres queue in the RabbitMQ Management Web UI

   > INSERT INTO presentation_example (payload) values ( 'this is a test') RETURNING row_id;
   
   > UPDATE presentation_example SET payload = 'Updated test message' WHERE row_id = 1;
   
   > DELETE FROM presentation_example WHERE row_id = 1;

6. Install client.sql in another database and keep track of connection info.

7. Install pika, the Python RabbitMQ client library:

   easy_install pika

Use
---
