from . import helpers
from .. import util, polyhedra, settings
import contextlib, sys, os


@contextlib.contextmanager
def _extended_sys_path(path):
	old_path = sys.path[:]
	sys.path.insert(0, path)
	
	yield
	
	sys.path[:] = old_path


class Configuration:
	def __init__(self, config_fn):
		self._config_fn = config_fn
	
	def apply(self, polyhedron : polyhedra.Polyhedron) -> helpers.Properties:
		properties = helpers.Properties()
		
		self._config_fn(settings.Settings(properties, polyhedron))
		
		return properties


def load_configuration(path):
	source = util.read_file(path)
	code = compile(source, path, 'exec', dont_inherit = True)
	
	with _extended_sys_path(os.path.dirname(source)):
		globals = { }
		
		exec(code, globals)
		
		config_fn = globals.get('config')
		
		if not callable(config_fn):
			raise ValueError('No function config() defined in config file {}.'.format(path))
		
		return Configuration(config_fn)
