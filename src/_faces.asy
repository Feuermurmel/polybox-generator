real offset = 100mm;

void face(path[] polygon, path[] cut, transform t) {
	fill(t * cut, red + white);
	draw(t * polygon, gray + 0.2mm);
	draw(t * cut, black + 0.01mm);
}

void face_id(pair center, string index, transform t) {
	label(index, t * center);
}

void edge_id(pair a, pair b, string index, transform t) {
	pair edge_center = t * ((a + b) / 2.0);
	path anchor = edge_center - unit(edge_center) * 0.3;
	transform r = rotate(90 + degrees(atan2(edge_center.y, edge_center.x)), edge_center);
	Label L = scale(0.5) * r * Label(index, edge_center);
	label(L, anchor);
}

void vertex_id(pair vertex, string index, transform t) {
	dot(t * vertex, gray + black + 1mm);
	label(index, t * vertex + unit(t * vertex) * 0.5);
}
