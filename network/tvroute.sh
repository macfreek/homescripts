#!/bin/vbash

# NOTE:
# This script is DEPRECATED.
# It is replaced by rfc3442-classless-routes


# Usage:
# Store this script as /config/scripts/tvroute.sh on your Ubiquiti router
# sudo chmod +x /config/scripts/tvroute.sh
# configure
# set system task-scheduler task updateIPTVroute executable path /config/scripts/tvroute.sh
# set system task-scheduler task updateIPTVroute interval 5m
# commit
# save
# exit

IPTV_INTF=eth5.4
KPNTV_SUBNET=213.75.112.0/21

# In case of problems, first renew your lease:
# renew dhcp interface $IPTV_INTF

# configured static route target
CUR_IP=$(cat /config/config.boot | grep $KPNTV_SUBNET -A1 | grep next-hop | awk '{ print $2}');

# static route target
NEW_IP=$(cat /var/run/dhclient_${IPTV_INTF}_lease | grep new_routers | awk -F= '{print $2}' | tr -d \');

if [ "$CUR_IP" = "$NEW_IP" ]; then
   echo Addresses the same
   exit 1;
fi

source /opt/vyatta/etc/functions/script-template

configure
delete protocols static route $KPNTV_SUBNET next-hop $CUR_IP
set protocols static route $KPNTV_SUBNET next-hop $NEW_IP
commit
save
exit

restart igmp-proxy
