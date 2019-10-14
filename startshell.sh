#!/bin/bash
i=$1
sed -i 's/^$/+ : '$i' : ALL/' /etc/security/access.conf
/usr/sbin/sssd -fd 2
sudo -H -u $i sh -c /bin/bash
