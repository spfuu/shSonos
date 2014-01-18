#!/bin/sh
#!/usr/bin/env python3

### BEGIN INIT INFO
# Provides: sonosservice
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: sonos server service
# Description: starts / stops / restart the sonos server service
### END INIT INFO

DIR=/usr/smarthome/plugins/sonos/server
DAEMON=$DIR/sonos_server.py
DAEMON_NAME=sonosserver
LOCALIP=192.168.178.31


# Root generally not recommended but necessary if you are using the Raspberry Pi GPIO from Python.
DAEMON_USER=admin

# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

do_start () {
touch $PIDFILE
chown $DAEMON_USER $PIDFILE
log_daemon_msg "Starting system $DAEMON_NAME daemon"
start-stop-daemon -v --start --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --background --startas $DAEMON -- --localip $LOCALIP
log_end_msg $?
}
do_stop () {
log_daemon_msg "Stopping system $DAEMON_NAME daemon"
start-stop-daemon --stop --pidfile $PIDFILE --retry 10
log_end_msg $?
}

case "$1" in

start|stop)
do_${1}
;;

restart|reload|force-reload)
do_stop
do_start
;;

status)
status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
;;
*)
echo "Usage: /etc/init.d/$DEAMON_NAME {start|stop|restart|status}"
exit 1
;;

esac
exit 0
