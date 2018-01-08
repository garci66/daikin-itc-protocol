#!/bin/bash
cd "${0%/*}" 
#echo `pwd`
cd daikin/
#echo `date` >>./calls.log
#echo "$@ $0" >> ./calls.log
#echo `pwd` >>./calls.log
#touch activehosts/$1
./daikinDiscover.py "$@"
