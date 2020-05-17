#!/bin/bash

###########################################################################
# Azure determine which cloud callee is in                                #
#                                                                         #
# Works by calling IMDS (aka.ms/imds) to get the location                 #
# and then look up the locations publishes in management.azure.com        #
###########################################################################

locations=`curl -s -H Metadata:True "http://169.254.169.254/metadata/instance/compute/location?format=text&api-version=2017-04-02"`

# Test regions
#locations="indiasouth"
#locations="usgovsouthcentral"
#locations="chinaeast"
#locations="germanaycentral"

endpoints=`curl -s https://management.azure.com/metadata/endpoints?api-version=2017-12-01` 
publicLocations=`echo $endpoints | jq .cloudEndpoint.public.locations[]`

if grep -q $locations <<< $publicLocations; then
    echo "PUBLIC"
    exit 1
fi

chinaLocations=`echo $endpoints | jq .cloudEndpoint.chinaCloud.locations[]`
if grep -q $locations <<< $chinaLocations; then
    echo "CHINA"
    exit 2
fi

usGovLocations=`echo $endpoints | jq .cloudEndpoint.usGovCloud.locations[]`
if grep -q $locations <<< $usGovLocations; then
    echo "US GOV"
    exit 3
fi

germanLocations=`echo $endpoints | jq .cloudEndpoint.germanCloud.locations[]`
if grep -q $locations <<< $germanLocations; then
    echo "GERMAN"
    exit 4
fi

echo "Unknown'
exit 0

