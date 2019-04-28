#!/bin/sh
cd ./pod042_bot
alembic -c ./alembic.ini upgrade head
