import time
import datetime

def get_string_time():
	timestamp = time.time()
	string_time = datetime.datetime.fromtimestamp(timestamp)\
					.strftime('%Y-%m-%d %H:%M:%S')
	return string_time