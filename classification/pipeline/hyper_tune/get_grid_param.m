%% Different hyperparameters
% Kernel parameters
sigma2 = linspace(10,20,5);
gamma = logspace(1e-3,0.1,5);

% Grid matrix from above
grid_matrix = combvec(sigma2, gamma);
grid.sigma2 = grid_matrix(1,:);
grid.gamma = grid_matrix(2,:);

%% Kalman filter (fixed for now)

opts = struct;
%rank
opts.Rank.C = 30;
opts.Rank.P = 1;
opts.Rank.x = 30;
opts.Rank.s = inf;
opts.Rank.K = 6;
% eps
opts.Eps.x = 0;
opts.Eps.P = 0;
opts.Eps.K = 0;
opts.Eps.s = 0.001;
opts.Eps.C = 0;
% other param
opts.R = 1;
opts.lambda = 1;
opts.p0 = 1;
opts.x0 = "zero";
opts.q = factor(1e4);

%% Options LSSVM
optsLSSVM = struct;
optsLSSVM.weighted = false;
optsLSSVM.method = "kalmanTT";
optsLSSVM.kalmanOpt = opts;

%% Save this shit
save('grid_param.mat', 'optsLSSVM','grid', '-mat')
