#!/bin/bash
cd "${0%/*}" 
cd daikin/
#echo -ne `date` >>./calls.log
#echo " $@" >> ./calls.log
./daikinChronPoller.py "$@"

