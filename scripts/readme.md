Files in this directory are used for different utilities around the database

eqdata_ml.py
=============
This is the most important file
This script is used to run seisbench ML models in for the earthquake data in the database.
set "DEFINE_NO_PLOT = True" when running in raspberry shake or non-display environment


configure_ml_database.py
========================
This file is the extact certain window of database and and create a new database using this
As an example, if we need to extract 2 seconds wave window database, you can use this script
It also includes the functionality like downsample which can be useful