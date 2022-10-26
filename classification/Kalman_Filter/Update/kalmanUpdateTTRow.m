function [x,P] = kalmanUpdateTTRow(x, y, C, P, R, Opts)
%kalmanUpdateTTRow(x, y, C, P, R, Opts) calculates the Kalman update 
%   for the given parameters. In this function the parameters are given as 
%   tensor-trains.
%
%INPUT
%   x (TensorTrain) : state-vector (as tensor-train).
%   y (vector)      : output variables.
%   C (TensorTrain) : row of C-matrix
%   P : covariance matrix previous time-step.
%   R : measurement covariance 
%   Options :   Kalman filter Options struct that contains the truncation
%               pars. (see setKalmanOptions.m)
%
%OUTPUT
%   x : updated state-vector.
%   P : updated covariance matrix.

%% Prediction step
P = (2-(1/Options.lambda)) * P;

%% Prediction
% output residual
v = y - dot(C,x);  %scalar
% Kalman steps
PC = P*C;   % P*C' (mat-vec product)
% PC = rounding(PC, Opts.Rank.s, Opts.Eps.s);
s = dot(C,PC) + R; 

K = PC*(1/s);     % rank K = rank PC 
K = rounding(K, Opts.Rank.K, Opts.Eps.K);
KSK = (K*K)*(-s); % -K*K' * S (S is scalar)
% KSK = rounding(KSK, Opts.Rank.K, Opts.Eps.K);

%% Update (summation)
x = x + K*v;
if any(rank(x) > 100)
    x = rounding(x, Opts.Rank.x, Opts.Eps.x);
end
% disp(max(rank(x)))

P = P + KSK;
P = rounding(P, Opts.Rank.P, Opts.Eps.x);


end