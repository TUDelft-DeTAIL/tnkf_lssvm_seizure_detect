function tt = shiftnorm(tt, n)
%SHIFTNORM  shifts the norm core of tt to n
%
%INPUT
%   tt
%   n
%OUTPUT
%   tt

tt_norm = tt.indexNorm;
if n == tt_norm
    return
end

if tt_norm == 0
    tt = orthogonalize(tt, n);
end

sz = tt.Size(:,2);
ranks = rank(tt);
d = ndims(tt);


if n < tt_norm
    for k = tt_norm:-1:n+1
        % right unfolding core
        core_R = reshape(tt.Cores{k},ranks(k),sz(k)*ranks(k+1));
        % QR 
        [Q,R] = qr(core_R',0);
        % contract core k-1 with R'
        core = reshape(tt.Cores{k-1},sz(k-1)*ranks(k-1),ranks(k));
        core = core*R';
        % calculate new rank
        ranks(k) = size(Q',1);
        % Replace cores
        tt.Cores{k} = reshape(Q',ranks(k),sz(k),ranks(k+1));
        tt.Cores{k-1} = reshape(core,ranks(k-1),sz(k-1),ranks(k));
    end

elseif n > tt_norm
    for k = tt_norm:n-1
        % left unfolding core
        core_L = reshape(tt.Cores{k},ranks(k)*sz(k),ranks(k+1));   
        % perform QR decomposition
        [Q,R] = qr(core_L,0);
        % save old rank
        oldRank = ranks(k+1);
        % calculate new rank
        ranks(k+1) = size(Q,2);
        % Replace cores
        tt.Cores{k} =  reshape(Q,ranks(k),sz(k),ranks(k+1));
        % 1-mode product
        core = reshape(tt.Cores{k+1},oldRank,sz(k+1)*ranks(k+2));
        core = R*core;
        tt.Cores{k+1} = reshape(core,size(R,1),sz(k+1),ranks(k+2));
    end
end

% Adjust size matrix
tt.Size = [ranks(1:d),sz,ranks(2:d+1)];
% Set norm index at pos n
tt.indexNorm = n;


end
% 
% 
% function shiftMPTnorm(mpt::MPT,n::Int64,dir::Int64)
% 
%         if dir == 1
%             Gl = unfold(mpt[n],[ndims(mpt[n])],"right");
%             ind   = 1;
%             F = qr(Gl);
%             R = Matrix(F.R); Q = Matrix(F.Q);
%         elseif dir == -1
%             Gr = unfold(mpt[n],[1],"left");
%             ind  = 3;
%             F = qr(Gr');
%             R = Matrix(F.R); Qt = Matrix(F.Q);
%             Q = Qt';
%         end
% 
%         mpt[n]       = reshape(Q, size(mpt[n]));
%         mpt[n+dir]   = nmodeproduct(R,mpt[n+dir],ind);
%         mpt.normcore = mpt.normcore + dir; 
% end
