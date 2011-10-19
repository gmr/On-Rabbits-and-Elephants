-- Trigger Function

CREATE OR REPLACE FUNCTION amqp_publish_trigger() RETURNS trigger AS
$amqp_publish_trigger$
"""On triggered action, publish the data to the RabbitMQ Broker using pg_amqp
in a JSON serialized object.

Handles trigger events generically, no need for specific customization unless
one is looking to omptimize message size and efficiency.

"""
import json
routing_key = '%s.%s' % (TD['table_schema'], TD['table_name'])
plan = plpy.prepare("SELECT amqp.publish(1, 'pgConf', $1, $2);", ["text", "text"])
plpy.execute(plan, [routing_key, json.dumps(TD)])
$amqp_publish_trigger$ LANGUAGE plpythonu;

-- Add the triggers

CREATE TRIGGER amqp_trigger_event
  AFTER INSERT OR UPDATE OR DELETE
  ON public.pgbench_accounts
  FOR EACH ROW
  EXECUTE PROCEDURE amqp_publish_trigger();

CREATE TRIGGER amqp_trigger_event
  AFTER INSERT OR UPDATE OR DELETE
  ON public.pgbench_branches
  FOR EACH ROW
  EXECUTE PROCEDURE amqp_publish_trigger();

CREATE TRIGGER amqp_trigger_event
  AFTER INSERT OR UPDATE OR DELETE
  ON public.pgbench_history
  FOR EACH ROW
  EXECUTE PROCEDURE amqp_publish_trigger();

CREATE TRIGGER amqp_trigger_event
  AFTER INSERT OR UPDATE OR DELETE
  ON public.pgbench_tellers
  FOR EACH ROW
  EXECUTE PROCEDURE amqp_publish_trigger();
