real offset = 100mm;

void face(path[] polygon, path[] cut, int column, int row) {
	transform t = shift(column * offset, -row * offset) * scale(20);
	
	fill(t * cut, red + white);
	draw(t * polygon, gray + 0.2mm);
	draw(t * cut, black + 0.01mm);
}
