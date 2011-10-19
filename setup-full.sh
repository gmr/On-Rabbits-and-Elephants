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
./rabbitmqadmin -u guest -p guest declare queue name=accounts durable=true
./rabbitmqadmin -u guest -p guest declare queue name=branches durable=true
./rabbitmqadmin -u guest -p guest declare queue name=history durable=true
./rabbitmqadmin -u guest -p guest declare queue name=tellers durable=true
./rabbitmqadmin -u guest -p guest declare queue name=watch durable=true
./rabbitmqadmin -u guest -p guest declare binding source=pgConf destination=accounts destination_type=queue routing_key=public.pgbench_accounts
./rabbitmqadmin -u guest -p guest declare binding source=pgConf destination=branches destination_type=queue routing_key=public.pgbench_branches
./rabbitmqadmin -u guest -p guest declare binding source=pgConf destination=history destination_type=queue routing_key=public.pgbench_history
./rabbitmqadmin -u guest -p guest declare binding source=pgConf destination=tellers destination_type=queue routing_key=public.pgbench_tellers
./rabbitmqadmin -u guest -p guest declare binding source=pgConf destination=watch destination_type=queue routing_key=public.*
easy_install pika
psql pgbench_server < server.sql
