from lib.settings import *


def config(s : Settings):
	# 4cm side length.
	s.scale_factor(40)
	
	s.edge(*s.polyhedron.face_by_id(0).face_cycle).tenon(RegularFingerTenon())
