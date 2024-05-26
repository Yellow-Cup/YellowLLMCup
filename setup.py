#!/usr/bin/env python
import environment
from yellowLLMDB import YellowLLMDB

with YellowLLMDB(environment.DBName) as db:
    db.initDB()

print("The DB is intitalized.")
