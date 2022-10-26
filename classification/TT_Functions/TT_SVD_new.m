function [TT] = TT_SVD_new(A,ranks,epsilon)
%TT_SVD(A,epsilon,'e') or TT_SVD(A,ranks,'r') returns the tensor-train
%   decomposition of a given tensor A.
%
%INPUT
%   A : d-dimensional tensor
%   epsilon (accuracy) OR ranks (vector with TT-ranks or scalar with max_rank)
%   option : char, 'e' for prescribed accuracy, 'r' for prescribed
%   maximal rank
%OUTPUT
%   TT : TensorTrain object

d = ndims(A); % number of dimensions of tensor
n = size(A);

% compute truncation parameter
if epsilon ~= Inf 
    delta = epsilon * normTens(A) * (1/sqrt(d-1));
    trunc_eps = true;
else
    trunc_eps = false;
    rank_e = Inf;
end

% check ranks
if isscalar(ranks)
    ranks = [1; ranks*ones(d-1,1);1];
    trunc_rank = true;
else
    if ranks(1) ~= 1
        error('First TT-rank must equal to 1');
    elseif ranks(end) ~= 1
        error('Last TT-rank must be equal to 1');
    elseif length(ranks) ~= d+1
        error("TT-ranks vector must be of length d+1")
    end
    trunc_rank = true;
end

%% Initialize
TT = TensorTrain;
TT.Size = zeros(d,3);   % matrix with sizes of tensor cores
TT.Cores = cell(d,1);
normE = zeros(d-1,1);
r = zeros(d,1);
r(1) = 1;

for k = 1:d-1
    % Matrix unfolding
    A = reshape(A,[r(k)*n(k),numel(A)/(r(k)*n(k))]) ;
    % truncated SVD using the maximum ranks
    [U,S,V] = svd(A,'econ');
    sigma = diag(S);
    rankC = nnz(sigma);
    
    if trunc_eps
        for rank_e = rankC:-1:1
            normE(k) = norm(sigma(rank_e:end));
            if normE(k) > delta
                break
            end
        end
    end
    r(k+1) = max(min([rankC, ranks(k+1), rank_e]),1);

    normE(k) = norm(sigma(r(k+1)+1:end));
    % New core
    TT.Cores{k} = reshape(U(:,1:r(k+1)),[r(k),n(k),r(k+1)]);
    TT.Size(k,:) = [r(k),n(k),r(k+1)];    % save size of core
    
    A = S(1:r(k+1),(1:r(k+1)))*V(:,1:r(k+1))';
end

TT.Cores{d} = A;   % last core

% output
TT.Size(d,:) = [size(TT.Cores{d}) 1];
TT.indexNorm = d;
normE = norm(normE);%sqrt(sum(normE.^2));
TT.normError = normE;
