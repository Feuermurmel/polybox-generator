import contextlib
from lib import export


_indentation_level = 0


def _format_call(module, *args, **kwargs):
	return '{}({})'.format(module, ', '.join([export.openscad_expression(i) for i in args] + ['{} = {}'.format(k, export.openscad_expression(v)) for k, v in kwargs.items()]))


def write_line(line, *args):
	print('\t' * _indentation_level + line.format(*args))


def write_call(module, *args, **kwargs):
	write_line('{};', _format_call(module, *args, **kwargs))


@contextlib.contextmanager
def write_group(module, *args, **kwargs):
	global _indentation_level
	
	write_line('{} {{', _format_call(module, *args, **kwargs))
	_indentation_level += 1
	
	yield
	
	_indentation_level -= 1
	write_line('}}')
