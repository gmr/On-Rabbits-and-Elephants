-- Insert a row into pg_amqp's definition table
INSERT INTO amqp.broker (host, vhost, username, "password") VALUES ('localhost', '/', 'guest', 'guest');

-- Table

CREATE TABLE presentation_example
(
  row_id serial NOT NULL PRIMARY KEY,
  occurred_at timestamp with time zone NOT NULL DEFAULT now(),
  payload text
);

-- Trigger Function, is ugly because it's creating a very fragile JSON formatted message

CREATE OR REPLACE FUNCTION demo_trigger() RETURNS trigger AS
$demo_trigger$
  DECLARE
    message text := '{"undefined": True}';
    result record;
  BEGIN
    IF TG_OP = 'DELETE' THEN
        message := $message${$message$ ||
          $message$"operation": "delete", $message$ ||
          $message$"event_time": "$message$ || CURRENT_TIMESTAMP || $message$",$message$ ||
          $message$"data": { $message$ || 
          $message$"row_id": $message$ || OLD.row_id || $message$,$message$ ||
          $message$"occurred_at": "$message$||OLD.occurred_at || $message$",$message$ ||
          $message$"payload": "$message$ || OLD.payload || $message$"$message$ ||
          $message$ } }$message$;
    ELSIF TG_OP = 'UPDATE' THEN
        message := $message${$message$ ||
          $message$"operation": "update", $message$ ||
          $message$"event_time": "$message$ || CURRENT_TIMESTAMP || $message$",$message$ ||
          $message$"old": { $message$ || 
          $message$"row_id": $message$ || OLD.row_id || $message$,$message$ ||
          $message$"occurred_at": "$message$||OLD.occurred_at || $message$",$message$ ||
          $message$"payload": "$message$ || OLD.payload || $message$"$message$ ||
          $message$ },$message$ ||
          $message$"new": { $message$ || 
          $message$"row_id": $message$ || NEW.row_id || $message$,$message$ ||
          $message$"occurred_at": "$message$||NEW.occurred_at || $message$",$message$ ||
          $message$"payload": "$message$ || NEW.payload || $message$"$message$ ||
          $message$ } }$message$;    
    ELSIF TG_OP = 'INSERT' THEN
        message := $message${$message$ ||
          $message$"operation": "insert", $message$ ||
          $message$"event_time": "$message$ || CURRENT_TIMESTAMP || $message$",$message$ ||
          $message$"data": { $message$ || 
          $message$"row_id": $message$ || NEW.row_id || $message$,$message$ ||
          $message$"occurred_at": "$message$|| NEW.occurred_at || $message$",$message$ ||
          $message$"payload": "$message$ || NEW.payload || $message$"$message$ ||
          $message$ } }$message$;    
    END IF;
    RAISE NOTICE 'Message: %', message;
    SELECT amqp.publish(1, 'postgres', 'publish_transactions', message) INTO result;
    RAISE NOTICE 'Result: %', result;
    RETURN NULL;
  END;
$demo_trigger$ LANGUAGE plpgsql;

-- Add the trigger

CREATE TRIGGER demo_trigger_event
  AFTER INSERT OR UPDATE OR DELETE
  ON presentation_example
  FOR EACH ROW
  EXECUTE PROCEDURE demo_trigger();
