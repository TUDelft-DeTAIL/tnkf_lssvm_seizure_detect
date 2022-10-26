function [TT] = TT_SVD_rank(A,r)
%TT_SVD_rank(A,r) return the tensor-train
%decomposition of a given tensor A.
%
%INPUT
%   A (d-dimensional tensor), r (vector or scalar with max. TT-ranks)
%OUTPUT
%   TT,  TT-cores in struct with parameters TT.cores and TT.Size
d = ndims(A); % number of dimensions of tensor
n = size(A);

if isscalar(r)
    r = [1; r*ones(d-1,1);1];
end


if r(1) ~= 1
    error('First TT-rank must equal to 1');
elseif r(end) ~= 1
    error('Last TT-rank must be equal to 1');
elseif length(r) ~= d+1
    error("TT-ranks vector must be of length d+1")
end

% Initialize
TT = TensorTrain;
TT.Size = zeros(d,3);   % matrix with sizes of tensor cores
TT.Cores = cell(d,1);
normE = zeros(d-1,1);


for k = 1:d-1
    % Matrix unfolding
    A = reshape(A,[r(k)*n(k),numel(A)/(r(k)*n(k))]) ;
    % truncated SVD using the maximum ranks
    [U,S,V] = svd(A,'econ');
    sigma = diag(S);
    rankC = nnz(sigma);
    if rankC < r(k+1) && rankC > 0
        r(k+1) = rankC;
    elseif rankC == 0
        r(k+1) = 1;
    end
    normE(k) = norm(sigma(r(k+1)+1:end));
    % delete columns past rank
    U = U(:,1:r(k+1)); V = V(:,1:r(k+1)); S = S(1:r(k+1),1:r(k+1));
    % New core
    TT.Cores{k} = reshape(U,[r(k),n(k),r(k+1)]);
    TT.Size(k,:) = [r(k),n(k),r(k+1)];  % save size of core
    
    A = S*V';
end

TT.Cores{d} = A;   % last core

% output
TT.Size(d,:) = [size(TT.Cores{d}) 1];
TT.indexNorm = d;
normE = norm(normE);%sqrt(sum(normE.^2));
TT.normError = normE;



