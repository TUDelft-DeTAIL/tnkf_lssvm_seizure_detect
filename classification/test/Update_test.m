

Nx = 100;
Ny = 50;

x = rand(Nx,1);
y = rand(Ny,1);

C = rand(Ny,Nx);
P = eye(Nx);

[x_test,P_test] = kalmanUpdateMat(x,y,C,P,0,0);

filt = KalmanFilter(x,P,0,[]);
for k = 1:Ny
    filt = filt.Update(y(k),C(k,:));
end

assert(all(ismembertol(filt.x,x_test, 0.001,'ByRows',true)))

assert(all(ismembertol(filt.P,P_test, 0.001,'ByRows',true)))