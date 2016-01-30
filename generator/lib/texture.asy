// Ensure 'correct' bounding boxes in eps file
size(1,1);
draw(circle((0.5,0.5), 0.5),blue+white);
//dot((0,0),blue+white);
draw((0,0)--(1,0),blue+white);
draw((0,0)--(0,1),blue+white);
real e = 0;
clip((e,e)--(e,1-e)--(1-e,1-e)--(1-e,e)--cycle);

// PostScript uses the point as its unit of length. However,
// unlike some of the other versions of the point, PostScript
// uses exactly 72 points to the inch. Thus:
// 1 point = 1/72 inch = 127/360 mm = 352.7 micrometer
