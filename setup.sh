createdb client
createdb server
psql client < client.sql
psql server < pg_amqp.sql
psql server < server.sql
