import math;

// TODO: Import this from _faces.asy
// What is the best way?
pen cut_pen = black + 0.01mm;

int n = 5;
real a = 1mm;
real R = a / (2*sin(pi/n));

real x = 0.5 * a;
real y = sqrt(R^2 - x^2);

pair center = (x,y);
real radius = 0.6 * R;

draw(circle(center, radius), cut_pen);
