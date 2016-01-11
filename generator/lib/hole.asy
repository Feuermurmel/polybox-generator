import math;


int gcd(int a, int b) {
  // Compute greatest common divisor of two numbers
  assert(a > 0, "Non-positive integer");
  assert(a > 0, "Non-positive integer");
  // Euclid's algorithm
  while(a != b) {
    if(a > b) {
      a = a - b;
    } else {
      b = b - a;
    }
  }
  return a;
}


int[] comprime(int a, int b) {
  // Compute the irreducible fraction of two numbers
  int g = gcd(a, b);
  while(g != 1) {
    a = quotient(a, g);
    b = quotient(b, g);
    g = gcd(a, b);
  }
  // Result: coprime integers a and b
  int[] r = {a, b};
  return r;
}


path hypotrochoid(real R, int p, int q, real d, int samples=200) {
  // https://en.wikipedia.org/wiki/Hypotrochoid
  // R:   Radius of fixed circle
  // r:   Radius of rolling circle
  // p/q: Ratio of radii: R/r = p/q
  // d:   Distance of tracing point
  real r = q*R/p;
  int n = comprime(p, q)[1];
  real dx = 2*pi / samples;
  int nn = n * samples;

  real theta = 0;
  real x[];
  real y[];
  for(int i=0; i <= nn; ++i) {
    theta = i*dx;
    x[i] = (R-r)*cos(theta) + d*cos(((R-r)/r)*theta);
    y[i] = (R-r)*sin(theta) - d*sin(((R-r)/r)*theta);
  }

  path c = (x[0], y[0]);
  for(int i=0; i <= nn; ++i) {
    c = c -- (x[i], y[i]);
  }
  return c;
}


// 6-gon hole
pen cut_pen = black + 0.01mm;

int n = 5;
real a = 1mm;
real x = 0.5 * a;
real y = 0.5 * sqrt(3) * a;
pair center = (x,y);

real R = 1;
int p = 6;
int q = 1;
real r = q*R/p;
real d = 0.5*r;

draw(scale(1,1.52752523165195)*shift(center)*scale(2.4)*hypotrochoid(R, p, q, d), cut_pen);
