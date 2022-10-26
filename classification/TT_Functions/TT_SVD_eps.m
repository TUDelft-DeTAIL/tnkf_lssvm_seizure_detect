function [TT] = TT_SVD_eps(A,epsilon)
%TT_SVD_eps(A,epsilon) returns the tensor-train
%   decomposition of a given tensor A.
%
%INPUT
%   A (d-dimensional tensor), epsilon (accuracy)
%OUTPUT
%   TT,  TT-cores in struct with parameters TT.cores and TT.Size

d = ndims(A); % number of dimensions of tensor
n = size(A);

% compute truncation parameter
delta = epsilon * normTens(A) * (1/sqrt(d-1));
r = zeros(d,1);
r(1) = 1;

TT = TensorTrain;
TT.Cores = cell(d,1);
TT.Size = zeros(d,3);   % matrix with sizes of tensor cores
normE = zeros(d-1,1);   % Frobenius norm of the error

for k = 1:d-1
    % Matrix unfolding
    A = reshape(A,[r(k)*n(k),numel(A)/(r(k)*n(k))]) ;
    
    % delta truncated SVD
    [U,S,V] = svd(A,'econ');     % singular values
    sigma = diag(S);
    rankC = nnz(sigma);
    
    for j = rankC:-1:1
        normE(k) = norm(sigma(j:end));
        if normE(k) > delta
            break
        end
    end
    r(k+1) = j; % rank of truncated svd
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
%normE = norm(normE);    %total error
TT.normError = norm(normE);


