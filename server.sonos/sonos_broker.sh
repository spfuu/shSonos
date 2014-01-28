#!/bin/sh
#!/usr/bin/env python3

export $PYTHONPATH
DAEMON=${PYTHONPATH}:/sonos_broker
DAEMON_NAME=sonosbroker

# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

do_start () {
touch $PIDFILE
#chown $DAEMON_USER $PIDFILE
log_daemon_msg "Starting system $DAEMON_NAME daemon"
start-stop-daemon -v --start --pidfile $PIDFILE --make-pidfile --startas $DAEMON --
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
