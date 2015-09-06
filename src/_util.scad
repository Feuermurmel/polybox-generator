inf = 1e6;
inf2 = 2 * inf;

module half_plane() {
	translate([0, inf]) {
		square(inf2, center = true);
	}
}

module half_space() {
	translate([0, 0, inf]) {
		cube(inf2, center = true);
	}
}

module _half_space_from_vertices(ax, ay, az, bx, by, bz, cx, cy, cz, flip) {
	multmatrix([[ax, bx, cx], [ay, by, cy], [az, bz, cz]]) {
		multmatrix([[1, 0, 0, 0], [0, 1, 0, 0], [-1, -1, 1, 1]]) {
			scale([1, 1, flip]) {
				half_space();
			}
		}
	}
}
