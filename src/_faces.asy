real offset = 100mm;

void cut_contour(path[] cut, transform t) {
	draw(t * cut, black + 0.01mm);
}


void face(path[] polygon, transform t) {
	fill(t * polygon, red + white);
	draw(t * polygon, red + 0.1mm);
}

void edges(path[] polygon, transform t) {
	draw(t * polygon, gray + 0.2mm);
}

void vertices(path[] polygon, transform t) {
	dot(t * polygon, gray + black + 0.8mm);
}


void face_id(pair center, string index, transform t) {
	label(index, t * center);
}

void edge_id(pair a, pair b, string index, transform t) {
	pair edge_center = t * ((a + b) / 2.0);
	pair anchor = 0.8 * edge_center;
	transform r = rotate(90 + degrees(atan2(edge_center.y, edge_center.x)));
	Label L = scale(0.5) * r * Label(index, anchor);
	label(L, anchor);
}

void vertex_id(pair vertex, string index, transform t) {
	label(index, t * vertex + unit(t * vertex) * 0.5);
}
