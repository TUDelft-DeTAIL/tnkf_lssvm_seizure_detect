function [A] = orthogonalize(A,n)
%orthogonalize(A,n) computes the n-orthogonalization of a TT-tensor A.
%
%INPUT
%   A : d-dimensional TT-tensor
%   n : index at which to orthogonalize. All cores 1...n-1 are left
%   orthogonal and all cores n...d are right orthogonal
%OUTPUT
%   A : n-orthogonalized version of TT-tensor A

if n == A.indexNorm
   return 
end

ranks = [1;A.Size(:,3)];
N = A.Size(:,2);
d = size(A.Size,1);

if n>d
   error("To compute n-orthogonalization of a d-dimensional TT-tensor, n<=d"); 
end

%% left orthogonalization
for k = 1:n-1
    % left unfolding core
    A_L = reshape(A.Cores{k},ranks(k)*N(k),ranks(k+1));   
    % perform QR decomposition
    [Q,R] = qr(A_L,0);
    % save old rank
    oldRank = ranks(k+1);
    % calculate new rank
    ranks(k+1) = size(Q,2);
    % Replace cores
    A.Cores{k} =  reshape(Q,ranks(k),N(k),ranks(k+1));
    % 1-mode product
    core = reshape(A.Cores{k+1},oldRank,N(k+1)*ranks(k+2));
    core = R*core;
    A.Cores{k+1} = reshape(core,size(R,1),N(k+1),ranks(k+2));
%    A.Cores{k+1} = ttm(A.Cores{k+1},R,1);
end

%% right orthogonalization

for k = d:-1:n+1
    % right unfolding core
    A_R = reshape(A.Cores{k},ranks(k),N(k)*ranks(k+1));
    % QR 
    [Q,R] = qr(A_R',0);
    % contract core k-1 with R'
    core = reshape(A.Cores{k-1},N(k-1)*ranks(k-1),ranks(k));
    core = core*R';
    % calculate new rank
    ranks(k) = size(Q',1);
    % Replace cores
    A.Cores{k} = reshape(Q',ranks(k),N(k),ranks(k+1));
    A.Cores{k-1} = reshape(core,ranks(k-1),N(k-1),ranks(k));
end

%%
% Adjust size matrix
A.Size = [ranks(1:d),N,ranks(2:d+1)];
% Set norm index at pos n
A.indexNorm = n;


