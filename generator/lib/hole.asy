import math;


int gcd(int a, int b) {
  // Assert a, b > 0
  while(a != b) {
    if(a > b) {
      a = a - b;
    } else {
      b = b - a;
    }
  }
  return a;
}


path epitrochoid(int R, int r, real d, int samples=200) {
  int n = quotient(max(R,r), gcd(R, r));
  real dx = 2*pi / samples;
  int nn = n*samples;

  real x[];
  real y[];
  for(int i=0; i <= nn; ++i) {
    real theta = i*dx;
    x[i] = (R+r)*cos(theta) - d*cos(((R+r)/r)*theta);
    y[i] = (R+r)*sin(theta) - d*sin(((R+r)/r)*theta);
  }

  path c = (x[0], y[0]);
  for(int i=1; i <= nn; ++i) {
    c = c -- (x[i], y[i]);
  }
  return c;
}


path hypotrochoid(int R, int r, real d, int samples=200) {
  int n = quotient(R, gcd(R, r));
  real dx = 2*pi / samples;
  int nn = n*samples;

  real x[];
  real y[];
  for(int i=0; i <= nn; ++i) {
    real theta = i*dx;
    x[i] = (R-r)*cos(theta) + d*cos(((R-r)/r)*theta);
    y[i] = (R-r)*sin(theta) - d*sin(((R-r)/r)*theta);
  }

  path c = (x[0], y[0]);
  for(int i=1; i <= nn; ++i) {
    c = c -- (x[i], y[i]);
  }
  return c;
}


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

int r = 1;
int R = 5;
real d = 0.6*r;

draw(shift(center)*scale(0.35)*rotate(18)*hypotrochoid(R, r, d), cut_pen);
