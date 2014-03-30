putio-downloader
================

putio-downloader is a python script which downloads automatically all your content from a specific location in your www.put.io account. The script can be installed easily as a ubuntu upstart service.

How to use it?
--------------

The main purpose of the script is to be used as part of the team Raspberry Pi + XBMC. 

Once putio-downloader has been set as a upstart service it can be configured to periodically check your put.io account looking for new content. The new content will be downloaded to the proper location, which ideally would be your XBMC media folder.

When everything will be running fine, all your new content in put.io will appear automatically in your XMBC library.

Installation
--------------

  - Clone the repo into your raspberry pi
  - Execute the installer script (install.sh)

This will install all the dependencies needed and will run putio-downloader as a upstart service.

The code will be installed in /opt/putio-downloaded

You can check the log file in: /var/log/upstart/putio-downloader.log

To start/stop/restart the service just type as sudo: restart/stop/start putio-downloader

Configuration
-------------

Config can be found in: /opt/putio-downloader/putio-downloader.ini

The description of every field is available as comments in the own file.


TODO:
-----

  - Check performance of queues and threading on raspberry pi
  - Add config options to limit download speed
  - Add config options to set a range of time to download
