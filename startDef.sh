#!/bin/bash
i=jovyan
sed -i 's/^$/+ : '$i' : ALL/' /etc/security/access.conf
/usr/sbin/sshd -e
cd /home/$i
sudo -H -u $i sh -c /bin/notebook.sh
while true
do echo here $(pwd) $(ps -ef | grep ssh) 
   sleep 15
done 
