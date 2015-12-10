
echo "****** Creating required directories:"
if [ ! -d /subscribe ]; then
	echo "****** /subscribe does not exist, will be created"
	mkdir /subscribe
	chown www-data:www-data /subscribe
fi
if [ ! -d /etc/uwsgi/tmp_ssl]; then
	echo "****** /etc/uwsgi/tmp_ssl does not exist, will be created"
	mkdir -p /etc/uwsgi/tmp_ssl
	chown www-data:www-data /etc/uwsgi/tmp_ssl
	chmod 700 /etc/uwsgi/tmp_ssl
fi

if [ ! -d /var/log/uwsgi]; then
	echo "****** /var/log/uwsgi does not exist, will be created"
	mkdir /var/log/uwsgi
	chown root:www-data /var/log/uwsgi
	chmod 770 /var/log/uwsgi
fi
echo "****** Cleaning previous installation"
rm -rf /opt/unbit/uwsgi/src
rm -rf /opt/unbit/uwsgi/plugins
mkdir -p /opt/unbit/uwsgi/src
mkdir -p /opt/unbit/uwsgi/plugins
echo "****** Cloning latest source"
git clone --branch uwsgi-2.0 https://github.com/unbit/uwsgi /opt/unbit/uwsgi/src
cd /opt/unbit/uwsgi/src
git pull
echo "****** Building uwsgi"
make uwsgi.it
cp -f uwsgi /opt/unbit/uwsgi/uwsgi
echo "****** Building python_plugin"
/opt/unbit/uwsgi/uwsgi --build-plugin plugins/python
cp python_plugin.so /opt/unbit/uwsgi/plugins

PLUGINS="router_redirect router_redis router_cache router_expires router_http router_metrics router_uwsgi router_memcached router_rewrite router_static rpc rrdtool signal spooler stats_pusher_statsd symcall xattr transformation_chunked transformation_gzip transformation_offload transformation_template transformation_tofile notfound logfile logpipe logsocket redislog cgi msgpack pypy geoip corerouter fastrouter http rawrouter forkptyrouter pty sslrouter router_basicauth alarm_curl curl_cron"
echo "****** Building other plugins"
for PNAME in $PLUGINS
do
	/opt/unbit/uwsgi/uwsgi --build-plugin plugins/${PNAME} >/dev/null
	cp ${PNAME}_plugin.so /opt/unbit/uwsgi/plugins/
done
echo "****** Building uwsgi-netlink"
/opt/unbit/uwsgi/uwsgi --build-plugin https://github.com/unbit/uwsgi-netlink
cp netlink_plugin.so /opt/unbit/uwsgi/plugins/

