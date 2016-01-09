// Pen whose stroke has correct properties
// for cuts laser cutter in 'vector' mode.
pen cut_pen = black + 0.01mm;

void cut_contour(path[] cut) {
	draw(cut, cut_pen);
}


void face(path[] polygon) {
	fill(polygon, red + white);
	draw(polygon, red + 0.1mm);
}

void edges(path[] polygon) {
	draw(polygon, gray + 0.2mm);
}

void vertices(path[] polygon) {
	dot(polygon, gray + black + 0.8mm);
}


void face_id(pair center, string index) {
	label(index, center);
}

void edge_id(pair a, pair b, string index) {
	pair edge_center = ((a + b) / 2.0);
	pair edge_direction = b - a;
	pair anchor = 0.8 * edge_center;
	transform r = rotate(degrees(atan2(edge_direction.y, edge_direction.x)));
	Label L = scale(0.5) * r * Label(index);
	label(L, anchor);
}

void vertex_id(pair vertex, string index) {
	label(index, vertex + unit(vertex) * 0.5);
}
