function [opts, sigma2, gamma, X_train, y_train] = generate_opts_struct(parameters, X_train, y_train)
%GENERATE_OPTS_STRUCT Summary of this function goes here
%   Detailed explanation goes here
[gamma, sigma2, opts] = load_parameters(parameters);
N = length(y_train);
opts.kalmanOpt.q = factor(N+1);
if max(opts.kalmanOpt.q) > 7
    warning("Largest mode due to quantization is %d which is > %d.", max(opts.kalmanOpt.q), maxQ)
    [q, N_new] = getQTTpar(N+1, maxQ);
    disp(["New N = " + num2str(N_new)])
    opts.kalmanOpt.q = q;
    % idx = randsample(N, N_new - 1);
    X_train = X_train(1:N_new-1,:);
    y_train = y_train(1:N_new-1,:);
end

end

