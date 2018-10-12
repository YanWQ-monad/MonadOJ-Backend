#!/bin/sh
mysql -u root -e 'CREATE DATABASE monadoj_test;'
mysql -u root -e "CREATE USER 'monadoj_test'@'localhost' IDENTIFIED BY 'MONADOJ TEST';"
mysql -u root -e "GRANT ALL ON monadoj_test.* TO 'monadoj_test'@'localhost';"
