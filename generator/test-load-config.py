from lib import util, config, polyhedra


@util.main
def main():
	polyhedron = polyhedra.Polyhedron.load_from_json('src/polyhedra/cube.json')
	
	configuration = config.load_configuration('src/config.py')
	settings = configuration.apply(polyhedron)
