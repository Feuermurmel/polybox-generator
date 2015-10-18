real offset = 100mm;

void face(path[] polygon, path[] cut, transform t) {
	fill(t * cut, red + white);
	draw(t * polygon, gray + 0.2mm);
	draw(t * cut, black + 0.01mm);
}

void vertex(pair vertex, int index, transform t) {
	dot(t * vertex, gray + black + 1mm);
	label((string) index, t * vertex + unit(t * vertex) * .5);
}
