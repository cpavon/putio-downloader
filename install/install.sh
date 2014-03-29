echo 'Installing dependencies...'
apt-get install python-iso8601
apt-get install python-requests

echo 'Installing put.io downloader service:'

echo 'coping files to /opt/putio_downloader....'
if [ -d "/opt/putio_downloader" ]; then
  rm -r /opt/putio-downloader
fi
mkdir /opt/putio-downloader
cp ../src/* /opt/putio-downloader
echo 'Done!'

echo 'Installing upstart putio_downloader service....'
cp putio-downloader.conf /etc/init
initctl reload-configuration
echo 'Done!'

echo 'Starting service....'
start putio-downloader
echo 'Done!'

echo 'putio_downloader has been installed sucessfully!!!'
echo 'You can check the log file in /var/log/upstart/putio-downloader.log'
