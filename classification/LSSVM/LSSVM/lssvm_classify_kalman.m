function [alpha, b, P] = lssvm_classify_kalman(X, Y, kernel_type, kernel_pars, gamma)


%% Initialize Kalman parameters
N = length(Y);
if size(X,1) ~= N
    error("Size of feature matrix not compatible with output vector.")
end
x_kalman = zeros(N+1,1);   % [b; alpha]
y_kalman = [0; ones(N,1)];
P_0 = eye(N+1);

%% Construct C-Matrix
C = zeros(N+1,N+1);
C(1,:) = [0, Y'];
C(:,1) = [0; Y];
Omega = (Y*Y').*kernel_matrix(X, kernel_type, kernel_pars); % Omega(i,j) = yi*yj*K(xi,xj)
C(2:end, 2:end) = Omega + diag(ones(N,1)/gamma);

%% Perform Kalman Update
[x_kalman, P] = kalmanUpdateMat(x_kalman, y_kalman, C, P_0, 0, 0);

%% Extract support vectors alpha and bias b
b = x_kalman(1);
alpha = x_kalman(2:end);
