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
