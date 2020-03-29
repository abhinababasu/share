COVID
=====

This script fetches the latest daily COVID data from http://covidtracking.com and then merges in state data like population. Finally the data output is a CSV with only a few relevant columns that can be charted using tools like excel.

Build
-----
Use
``` bash
go build .
```

Running
-------
Run using 
``` bash
go run . > daily.csv
```

Work with the csv in excel etc.