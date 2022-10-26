

N = 10;
X = rand(N,3);
y = [1,1,1,-1,-1,1,-1,1];

[Xr1, yr1] = alternate_data(X, y, 1, 1);
tol = 1e-3;

assert(all(ismembertol(X(1,:),Xr1(2,:),tol)))
assert(all(ismembertol(X(2,:), Xr1(4,:),tol)))
assert(all(ismembertol(X(4,:), Xr1(1,:), tol)))
assert(all(ismembertol(X(4,:), Xr1(7,:), tol)))
assert(y(1) == yr1(2))
assert(y(4) == yr1(1))

[Xr2, yr2] = alternate_data(X, y, 2, 2);

assert(all(ismembertol(X(1,:), Xr2(3,:),tol)))
assert(all(ismembertol(X(2,:), Xr2(4,:),tol)))
assert(all(ismembertol(X(4,:), Xr2(1,:), tol)))
assert(all(ismembertol(X(5,:), Xr2(2,:), tol)))
assert(all(yr2(1:2) == -1))
assert(all(yr2(3:4) == 1))

[Xr3, yr3] = alternate_data(X, y, 3, 1);

assert(all(ismembertol(X(1,:), Xr3(4,:),tol)))
assert(all(ismembertol(X(2,:), Xr3(8,:),tol)))
assert(all(ismembertol(X(4,:), Xr3(1,:), tol)))
assert(all(ismembertol(X(5,:), Xr3(2,:), tol)))
assert(all(yr3(1:3) == -1))
assert(all(yr3(4) == 1))