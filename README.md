# README #

Script to automate some manual manipulation I had to do to akabei databases due to https://chakraos.org/bugtracker/index.php?do=details&task_id=1498 . The script takes the repository name as input:

* downloads the akabei database from the remote server
* uncompresses it
* executes a series of SQL queries to correct the group tables, and verifies the result
* compresses it back and signs the archive with your key.

### Dependencies ###

* python3
* urllib
* sqlite3