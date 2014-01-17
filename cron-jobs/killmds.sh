#!/bin/sh
# Pause resource-consuming mds and mdworker, the indexers for SpotLight
# This gives them 0% CPU time. Killing (terminating) these processes 
# altogether is not useful, as launchd relaunches them.
sudo killall -STOP mds mdworker mds_stores mdflagwriter
