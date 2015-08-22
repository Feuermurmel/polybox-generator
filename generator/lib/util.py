import math, numpy


# "We get further from truth when we obscure what we say." -- https://www.youtube.com/watch?v=FtxmFlMLYRI
tau = 2 * math.pi


def normalize(v):
	return v / numpy.linalg.norm(v)
