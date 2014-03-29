import Queue
import threading
from threading import Thread
import os
import shutil
import time
import putio2
import ConfigParser
import logging
import tempfile



# Configuration constants
CONFIG_FILE = "putio_downloader.ini"
MOVIES_SECTION = 'MOVIES'
SERIES_SECTION = 'SERIES'
PUTIO_FOLDER = 'putio_folder'
DESTINATION_FOLDER = 'destination_folder'

class PutioDownloader():

	DOWNLOAD_QUEUE = Queue.Queue()
	all_files_in_queue = []

	def __init__(self):
		# Read config file
		self._read_config()
		# Init put.io client API
		self._init_putio_client()
		# Create temp folder
		self.temp_folder = tempfile.mkdtemp()
		# Init listener for the download queue
		self._init_queue_listener()

	def _read_config(self):
		self.config = ConfigParser.ConfigParser()
		file = open(CONFIG_FILE)
		self.config.readfp(file)

	def _init_putio_client(self):
		token = self.config.get('PUTIO_GENERAL', 'access_token')
		self.client = putio2.Client(token)

	def _init_queue_listener(self):
		max_concurrent_downloads = self.config.getint('PUTIO_GENERAL', 'max_concurrent_downloads')
		thread = Thread(target=self._async_download_queue_listener, args=(max_concurrent_downloads, ))
		thread.start()

	def _async_download_queue_listener(self, max_concurrent_downloads):
		# This semaphore will mark the limit of concurrent executors in this queue
		pool = threading.BoundedSemaphore(max_concurrent_downloads)
		while True:
			time.sleep(0.01)
			# Wait for the semaphore
			pool.acquire()
			# Get file next file in the queue
			file = self.DOWNLOAD_QUEUE.get()
			# Starts download
			self._download(file)
			# Mark task as done
			self.DOWNLOAD_QUEUE.task_done()
			pool.release()


	def start(self):
		while True:
			try:
				series_enabled = self.config.getboolean(SERIES_SECTION, 'enabled')
				movies_enabled = self.config.getboolean(MOVIES_SECTION, 'enabled')

				if movies_enabled:
					print("Checking for new movies.....")
					self._check_new_files(MOVIES_SECTION)
					print("Movies checked!")

				if series_enabled:
					print("Checking for new series.....")
					self._check_new_files(SERIES_SECTION)
					print("Series checked!")

				delay = self.config.getint('PUTIO_GENERAL', 'checking_schedule_minutes')

				# FIXME: this is a horrible hack... but it works. a TODO for the future: use crontab in Ubuntu or Alarms in python.
				time.sleep(delay * 60)
			except:
				# Sometimes putio API fails... I don't wanna stop the service in this case, so I wait and retry
				time.sleep(60)
				pass

	def _check_new_files(self, section):
		putio_folder = self.config.get(section, PUTIO_FOLDER)
		dst = self.config.get(section, DESTINATION_FOLDER)
		print("Checking items to download in %s" % putio_folder)

		already_downloaded = self._get_already_donwloaded(dst)

		# Find the id of the putio folder
		putio_path = putio_folder.split('/')
		parent_id = None
		for path in putio_path:
			files = self.client.File.list(parent_id=parent_id, as_dict=True)
			for key, value in files.items():
				if value.name == path:
					parent_id = value.id

		files_putio = self._find_files_from_directory(parent_id)
		files_to_download = self._find_new_files(files_putio, already_downloaded)
		if not files_to_download:
			logging.warning("Nothing to download!")
			return

		self._send_to_download_queue(files_to_download, dst)


	def _find_new_files(self, putio_files, already_downloaded):
		new_files = []
		for file in putio_files:
			if not file['file'].name in already_downloaded:
				new_files.append(file)
		return new_files

	def _get_already_donwloaded(self, path):
		already_downloaded = []
		for path, subdirs, files in os.walk(path):
			for name in files:
				already_downloaded.append(name)
		print '[INFO] Already downloaded files: %s' % already_downloaded
		return already_downloaded


	def _find_files_from_directory(self, parent_id, path=""):
		files_to_download = []
		files = self.client.File.list(parent_id=parent_id)
		for file in files:
			type = file.content_type
			if 'directory' in type:
				files_to_download.extend(self._find_files_from_directory(file.id, path="%s/%s" % (path, file.name)))
			else:
				file_dic = {'file': file, 'path': path}
				files_to_download.append(file_dic)
		return files_to_download


	def _send_to_download_queue(self, files, dst):
		for f in files:
			file_to_download = f['file']
			destination_path = dst + f['path']
			download_data = {'file': file_to_download, 'dst': destination_path}
			if not file_to_download.name in self.all_files_in_queue:
				self.DOWNLOAD_QUEUE.put(download_data)
				self.all_files_in_queue.append(file_to_download.name)


	def _download(self, download_data):
		file = download_data.get('file')
		dst = download_data.get('dst')
		d = os.path.dirname(dst)
		if not os.path.exists(d):
			os.makedirs(d)
		if not os.path.exists(dst):
			os.makedirs(dst)
		print "Downloading file %s..." % file.name.encode('utf8')
		file.download(dest=self.temp_folder)
		print "Download finished successfully!!"
		print("Moving to destination folder....")
		shutil.move('%s/%s' % (self.temp_folder, file.name), '%s/%s' % (dst, file.name))
		print("Done!")


if __name__ == '__main__':
	downloader = PutioDownloader()
	downloader.start()