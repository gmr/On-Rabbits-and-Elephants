#!/bin/bash
dropdb pgbench_server
dropdb pgbench_client
./rabbitmqadmin -u guest -p guest delete exchange name=pgConf
./rabbitmqadmin -u guest -p guest delete queue name=accounts
./rabbitmqadmin -u guest -p guest delete queue name=branches
./rabbitmqadmin -u guest -p guest delete queue name=history
./rabbitmqadmin -u guest -p guest delete queue name=tellers
./rabbitmqadmin -u guest -p guest delete queue name=watch
