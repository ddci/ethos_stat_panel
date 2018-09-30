#!/bin/sh
rm -f /tmp/*.pid
rm -f /app/*.pid
exec "$@"