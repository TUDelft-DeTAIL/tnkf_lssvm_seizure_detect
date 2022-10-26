function [x_new,P] = kalmanUpdateMat(x_old,y,C,P,W,R)
%kalmanUpdateMat(x,y,C,P,W,R) calculates the Kalman update for the given
%   parameters. In this function the parameters are given as vectors and
%   matrices (NOT tensor-trains).

%% Prediction step
% x = A x + B u = x  and P = A P A' + W = P + W
P = P + W;

%% Update step
% Measurement residual
v = y - C*x_old;
% Residual covariance matrix
S = C*P*C' + R; % noise-free measurement
% Kalman gain
K = P*C'/S;

%% Update estimates
x_new = x_old + K*v;
P = P - K*S*K';





