function [A] = rounding(A, ranks, epsilon)
%rounding(A,epsilon,'e') OR rounding(A,rank,'r') performs the TT-rounding 
%   of a given TT A, with prescribed accuracy epsilon or with maximum
%   rank(s).
%
%INPUT
%   A : tensor-train with sub-optimal ranks
%   epsilon/rank : prescribed accuracy epsilon or maximum rank(s).
%   opt : 'e' or 'r' for epsilon or rank resp.
%OUTPUT
%   A : tensor-train with optimal ranks


% d = size(A.Size,1);
% maxRank = A.maxRank;
% desRank = A.desRank;
%% perform right-to-left orthogonalization
A = orthogonalize(A,1);

%% Perform compression step
% switch opt
%     case 'e'
%         
%         A = compression_eps(A,par,d);
%         
%     case 'r'
%         
%         A = compression_rank(A,par,d);
% end

% check if compression is needed
if all(rank(A) <= ranks) && epsilon == inf
    return 
end

A = compression_new(A, ranks, epsilon);


end

function [A, normE] = compression_new(A, ranks, epsilon)
%% Compression with both ranks and epsilon as input

d = ndims(A);
n = A.Size(:,2);
normE = zeros(d-1,1);
r = [1;A.Size(:,3)];

% add error calculation
if A.normError ~= -1
    errCalc = true;
else
    errCalc = false;
end

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

%% Truncate
% initialize:

for k = 1:d-1
    % compute truncated SVD
    Ak = reshape(A.Cores{k},r(k)*n(k),r(k+1));
    [U,S,V] = svd(Ak,'econ');
    sigma = diag(S);
    oldRank = r(k+1);
    rankC = nnz(sigma);
    
    if trunc_eps
        for rank_e = rankC:-1:1
            normE(k) = norm(sigma(rank_e:end));
            if normE(k) > delta
                break
            end
        end
    end
    % Set new ranks as minimum of possible ranks
    r(k+1) = max(min([rankC, ranks(k+1), rank_e]),1);

    normE(k,1) = norm(sigma(r(k+1)+1:end));
    
    % delete columns past rank
    U = U(:,1:r(k+1));
    V = V(:,1:r(k+1));
    S = S(1:r(k+1),1:r(k+1));
    % calculate new cores
    A.Cores{k} = reshape(U,r(k),n(k),r(k+1));
    % 1-mode product core(k+1) x_1 (VS)'
    core = reshape(A.Cores{k+1},oldRank,n(k+1)*r(k+2));
    VS = (V*S)';
    core = VS*core;
    A.Cores{k+1} = reshape(core,size(VS,1),n(k+1),r(k+2));
   
end

% Set new size
A.Size = [r(1:d),n,r(2:d+1)];
A.indexNorm = d;
% output error
if errCalc
    A.normError = norm(normE)+A.normError;
end

end


function [A,normE] = compression_eps(A,epsilon,d)
%% compression of orthogonalized representation
% initialize parameters
r = [1;A.Size(:,3)];
n = A.Size(:,2);
normE = zeros(d-1,1);
delta = (epsilon/sqrt(d-1))*norm(A);

% add error calculation
if A.normError ~= -1
    errCalc = true;
else
    errCalc = false;
end

for k = 1:d-1
    % compute delta-truncated SVD
    Ak = reshape(A.Cores{k},r(k)*n(k),r(k+1));
    [U,S,V] = svd(Ak,'econ');
    sigma = diag(S);
    rank_Ak = max(1,nnz(sigma));
    oldRank = r(k+1);
    for j = rank_Ak:-1:1
        if norm(sigma(j:end)) > delta
            break
        end
    end
    % set new rank
    r(k+1) = j;
    normE(k,1) = norm(sigma(r(k+1)+1:end));
    
    % delete columns past rank
    U = U(:,1:r(k+1));
    V = V(:,1:r(k+1));
    S = S(1:r(k+1),1:r(k+1));
    % calculate new cores
    A.Cores{k} = reshape(U,r(k),n(k),r(k+1));
    % 1-mode product core(k+1) x_1 (VS)'
    core = reshape(A.Cores{k+1},oldRank,n(k+1)*r(k+2));
    VS = (V*S)';
    core = VS*core;
    A.Cores{k+1} = reshape(core,size(VS,1),n(k+1),r(k+2));
   
end

A.Size = [r(1:d),n,r(2:d+1)];
A.indexNorm = d;
% output error
if errCalc
    A.normError = norm(normE)+A.normError;
end
end


function [A,normE] = compression_rank(A,ranks,d)
%% compression of orthogonalized representation
% initialize parameters
n = A.Size(:,2);
normE = zeros(d-1,1);
r = rank(A);

if isscalar(ranks)
    ranks = [1; ranks*ones(d-1,1);1];
end

if A.normError ~= -1
    errCalc = true;
else
    errCalc = false;
end

for k = 1:d-1
    % compute delta-truncated SVD
    Ak = reshape(A.Cores{k},r(k)*n(k),r(k+1));
    [U,S,V] = svd(Ak,'econ');
    sigma = diag(S);
    rank_Ak = nnz(sigma);
    oldRank = r(k+1);
    if rank_Ak < ranks(k+1) && rank_Ak > 0
        r(k+1) = rank_Ak;
    elseif rank_Ak == 0
        r(k+1) = 1;
    else
        r(k+1) = ranks(k+1);
    end
    % calculate error
    if errCalc
        normE(k,1) = norm(sigma(r(k+1)+1:end));
    end
    % delete columns past rank
    U = U(:,1:r(k+1));
    V = V(:,1:r(k+1));
    S = S(1:r(k+1),1:r(k+1));
    % calculate new cores
    A.Cores{k} = reshape(U,r(k),n(k),r(k+1));
    % 1-mode product of core and (V*S)'
    core = reshape(A.Cores{k+1},oldRank,n(k+1)*r(k+2));
    VS = (V*S)';
    core = VS*core;
    % reshape--o--
    %          | 
    A.Cores{k+1} = reshape(core,size(VS,1),n(k+1),r(k+2));
end

A.Size = [r(1:d),n,r(2:d+1)];

A.indexNorm = d;
% output error
if errCalc
    A.normError = norm(normE)+A.normError;
end
end