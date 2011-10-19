#!/bin/bash
dropdb pgbench_server
dropdb pgbench_client
./rabbitmqadmin -u guest -p guest delete exchange name=pgConf
