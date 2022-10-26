function LS = fit_kalman_row(LS)
%fit_kalmanTT(LS)

N = length(LS.y_train);
% opts = LS.Options.kalmanOpt;
x = zeros(N+1,1);
P = eye(N+1);
R = 0;
filt = KalmanFilter(x, P, R, []);
y_kalman = [0; ones(N,1)];
% k = 0
C = [0, LS.y_train'];
filt = filt.Update(y_kalman(1), C);
% [x,P] = kalmanUpdateMat(x,y_kalman(1),C,P,0,R);
% k > 0 
for k = 1:N
    C = [LS.y_train(k), LS.kernel_row(k)];
    filt = filt.Update(y_kalman(k+1), C);
%     [x,P] = kalmanUpdateMat(x,y_kalman(k+1),C,P,0,R);
end

% x = TT2Vec(filt.x);
LS.b = filt.x(1);
LS.alpha = filt.x(2:N+1);

end