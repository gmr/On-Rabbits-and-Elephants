#!/bin/bash
createdb pgbench_client
pgbench -i pgbench_client
easy_install pika
