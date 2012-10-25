#!/bin/sh
# To use sh csv2fixture.sh ~/Downloads/Thing2*.csv will create a json fixture of all the  ~/Downloads/Thing2*.csv files on stdout
names=""
base=`dirname $0`
while [ "$1" != "" ]
do
    for i in $1
    do
        f=`echo $1|sed "s/ //g"`
        b=`basename $f`
        op="/tmp/$b.json"
        cat "$1" | /usr/bin/python $base/csv2json_fixture.py > $op
        names="$names $op"
    done
    shift
done
/usr/bin/python $base/concat_json.py $names