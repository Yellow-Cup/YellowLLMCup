#!/usr/bin/env python
import environment
from yellowDB import YellowDB

with YellowDB(environment.DBName) as db:
    db.initDB()

print("The DB is intitalized.")
