#!/bin/bash

# Download raw latest data
curl -s http://covidtracking.com/api/states.csv > raw.csv


# keep the header, but remove states above 60 (e.g. territories)
# also sort on state code so that it is easy to join with state population
cat raw.csv | awk -F, -v OFS=',' '
 FNR==1{print $17, $1, $2, $9, $11, $12, $16}
 $17<60{print $17, $1, $2, $9, $11, $12, $16}
' | sort -k1 -n --field-separator=',' > states.csv

