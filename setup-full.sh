#!/bin/bash
createdb pgbench_client
createdb pgbench_server
pgbench -i pgbench_client
pgbench -i pgbench_server
createlang plpythonu pgbench_server
psql pgbench_server -c "CREATE EXTENSION amqp;"
psql pgbench_server -c "INSERT INTO amqp.broker (host,vhost,username,password) VALUES ('localhost', '/', 'guest', 'guest');"
curl -o rabbitmqadmin http://guest:guest@localhost:55672/cli/rabbitmqadmin
chmod u+x rabbitmqadmin
./rabbitmqadmin -u guest -p guest declare exchange name=pgConf type=topic
easy_install pika
psql pgbench_server < server.sql
