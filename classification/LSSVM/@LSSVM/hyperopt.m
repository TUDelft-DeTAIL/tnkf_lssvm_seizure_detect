function [LS] = hyperopt(LS, method, K, varargin)
%gamma, kernel_par, TT_ranks)
%HYPEROPT optimizes the hyperparameters of the LSSVM class using K-fold
%   crossvalidation. 
%   


cv = cvpartition(LS.y_train, "KFold", K);

switch method
    case "gridsearch"
        LS = gridsearch(LS, cv, varargin); %gamma, kernel_par, TT_ranks);
    case "random_grid"

    otherwise
        error("Specified hyperparameter optimization method not valid.")
end


end

function LS = gridsearch(LS, cv, varargin) %gamma, kernel_par, TT_ranks)

% if nargin ~= 5
%     error('Incorrect number of input variables specified')
% end
varargin = varargin{1};
if length(varargin) == 3
    gamma = varargin{1};
    kernel_par = varargin{2};
    TT_ranks = varargin{3};
    par_matrix = combvec(gamma, kernel_par, TT_ranks); % rows are the different pars;
    results = zeros(size(par_matrix,2),1);
elseif length(varargin) == 1
    par_matrix = varargin{1};
    gamma = unique(par_matrix(1,:));
    kernel_par = unique(par_matrix(2,:));
    TT_ranks = unique(par_matrix(3,:));

end

if length(gamma) == 1 && length(kernel_par) == 1 && length(TT_ranks) == 1
    LS.gamma = gamma;
    LS.kernel_pars = kernel_par;
    LS.Options.kalmanOpt.Rank.x = TT_ranks;
    LS.Options.kalmanOpt.Rank.C = TT_ranks;
    return
end

% results = zeros(length(gamma), length(kernel_par), length(TT_ranks));
% for g = 1:length(gamma)
%     for k = 1:length(kernel_par)
%         for r = 1:length(TT_ranks)
%             LS.gamma = gamma(g);
%             LS.kernel_pars = kernel_par(k);
%             LS.Options.kalmanOpt.Rank.x = TT_ranks(r);
%             LS.Options.kalmanOpt.Rank.C = TT_ranks(r);
%             LS = LS.crossval(cv);
%             results(g,k,r) = mean(LS.results.accuracy);
%         end
%     end
% end
gamma = par_matrix(1,:);
kernel_par = par_matrix(2,:);
TT_ranks = par_matrix(3,:);
opts = LS.Options;
X_train = LS.X_train;
y_train = LS.y_train;
kernel = LS.kernel_type;

parfor i = 1:size(par_matrix,2)
    temp = LSSVM(X_train, y_train, kernel, ...
        gamma(i), kernel_par(i), opts);
    temp.Options.kalmanOpt.Rank.x = TT_ranks(i);
    temp.Options.kalmanOpt.Rank.C = TT_ranks(i);
    temp = temp.crossval(cv);
    results(i) = mean(temp.results.accuracy);
end

[m, id_opt] = max(results);
disp("Gridsearch ended with max accuracy at " + num2str(m))

% [g, k , r] = ind2sub(size(results), id_opt);
LS.gamma = par_matrix(1,id_opt);
LS.kernel_pars = par_matrix(2,id_opt);
LS.Options.kalmanOpt.Rank.x = par_matrix(3,id_opt);
LS.Options.kalmanOpt.Rank.C = par_matrix(3,id_opt);
save_file = ['./results/results_gamma' sprintf('%.f',unique(gamma)) ...
    '_sigma' sprintf('%.f', unique(kernel_par)) '.mat'];
save(save_file, 'results', 'par_matrix')

end