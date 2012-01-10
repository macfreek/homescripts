#!/bin/sh
# Kill resource-consuming mds and mdworker, the indexers for SpotLight
while true
do
    killall mds mdworker 2> /dev/null
    sleep 1
done