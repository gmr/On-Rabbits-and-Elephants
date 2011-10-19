#!/bin/bash
createdb pgbench_server
pgbench -i pgbench_server
easy_install pika
