function [alpha, b] = lssvm_classify(X_train, y_train, kernel_type, kernel_pars, gamma)
%lssvm_classify(X_train, y_train, kernel_type, kernel_pars, gamma)
%     train a lssvm classifier.
%
%
%
%% Initialize Kalman parameters
N = length(y_train);
if size(X_train,1) ~= N
    error("Size of feature matrix not compatible with output vector.")
end
u = [0; ones(N,1)];

%% Construct C-Matrix
C = zeros(N+1,N+1);
C(1,:) = [0, y_train'];
C(:,1) = [0; y_train];
Omega = (y_train*y_train').*kernel_matrix(X_train, kernel_type, kernel_pars); % Omega(i,j) = yi*yj*K(xi,xj)
if length(gamma) == 1
    C(2:end, 2:end) = Omega + diag(ones(N,1)/gamma);
elseif length(gamma) == 2
    i_noseiz = (y_train == -1);
    i_seiz = (y_train == 1);
    new_gamma = zeros(length(y_train),1);
    new_gamma(i_seiz) = gamma(2);
    new_gamma(i_noseiz) = gamma(1);
    C(2:end, 2:end) = Omega + diag(1./new_gamma);
elseif length(gamma) == length(y_train)
    C(2:end, 2:end) = Omega + diag(1./gamma);
else
    error("invalid gamma to calculate kernel matrix")
end

% solve linear system
a = C\u;

%% Extract support vectors alpha and bias b
b = a(1);
alpha = a(2:end);
