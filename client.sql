CREATE TABLE presentation_consumer_table
(
  consumer_row_id serial primary key not null,
  changed_at timestamp with time zone NOT NULL DEFAULT now(),
  row_id int4,
  occurred_at timestamp with time zone,
  payload text
);