function [gamma, sigma2, opts] = load_parameters(parameters_file)
%LOAD_PARAMETRS Load the LSSVM and Kalman filter hyperparameters.
%   convert null to inf
%   output: gamma, sigma2, opts (LSSVM options block)

s = load_json(parameters_file);
gamma = s.gamma;
sigma2 = s.sigma2;
opts = s.opts;

% Check for rank = null and convert to inf
fnames = fieldnames(opts.kalmanOpt.Rank);
for k = 1:numel(fnames)
    if( isempty(opts.kalmanOpt.Rank.(fnames{k})) )
        opts.kalmanOpt.Rank.(fnames{k}) = inf;
    end
end

end

