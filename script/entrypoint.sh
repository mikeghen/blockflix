#!/usr/bin/env bash
sleep 10 # Wait for Postgres

flask db upgrade
if [ "$FLASK_DEBUG" = "1" ] ; then
  flask seed
fi

exec flask run --host=0.0.0.0
