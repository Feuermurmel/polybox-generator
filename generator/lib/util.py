import sys, os, math, contextlib, inspect


# "We get further from truth when we obscure what we say." -- https://www.youtube.com/watch?v=FtxmFlMLYRI
tau = 2 * math.pi


def log(message, *args):
	print(message.format(*args), file = sys.stderr)


class UserError(Exception):
	"""
	Error that should be reported to the user. Throwing this exception will not print a stack trace.
	"""
	
	def __init__(self, message, *args):
		super().__init__(message.format(*args))


def main(fn):
	"""
	Decorator for "main" functions. Decorates a function that should be called when the containing module is run as a script (e.g. via python -m <module>).
	"""
	
	frame = inspect.currentframe().f_back
	
	def wrapped_fn(*args, **kwargs):
		try:
			fn(*args, **kwargs)
		except UserError as e:
			log('Error: {}', e)
			sys.exit(1)
		except KeyboardInterrupt:
			sys.exit(2)
	
	if frame.f_globals['__name__'] == '__main__':
		wrapped_fn(*sys.argv[1:])
	
	# Allow the main function also to be called explicitly
	return wrapped_fn


@contextlib.contextmanager
def empty_context():
	yield


@contextlib.contextmanager
def _temp_file_path(path):
	temp_path = path + '~'
	dir_path = os.path.dirname(path)
	
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)
	
	yield temp_path
	
	os.rename(temp_path, path)


@contextlib.contextmanager
def reading_file(path):
	with open(path, 'rb') as file:
		yield file


@contextlib.contextmanager
def reading_text_file(path):
	with open(path, 'r', encoding = 'utf-8') as file:
		yield file


def read_file(path):
	with reading_file(path) as file:
		return file.read()


def read_text_file(path):
	with reading_text_file(path) as file:
		return file.read()


@contextlib.contextmanager
def writing_file(path):
	with _temp_file_path(path) as temp_path, open(temp_path, 'wb') as file:
		yield file
		
		file.flush()
		os.fsync(file.fileno())


@contextlib.contextmanager
def writing_text_file(path):
	with _temp_file_path(path) as temp_path, open(temp_path, 'wt', encoding = 'utf-8') as file:
		yield file
		
		file.flush()
		os.fsync(file.buffer.fileno())


def write_file(path, data : bytes):
	with writing_file(path) as file:
		file.write(data)


def write_text_file(path, data : str):
	with writing_text_file(path) as file:
		file.write(data)
