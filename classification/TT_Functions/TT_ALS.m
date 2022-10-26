function [tt] = TT_ALS(tens, tt_0, epsilon, maxiter)
%TT_ALS performs TT-ALS procedure to obtain TT from given initial TT
%
%INPUT
%   tens
%   tt_0
%   epsilon
%   maxiter
%
%OUTPUT
%   tt

d = ndims(tens);
sz = size(tens);
if nargin <= 3
    maxiter = 10;
end

if tt_0.indexNorm ~= d
    tt_0 = orthogonalize(tt_0, d);
end

tens_norm = normTens(tens)^2;
% Sweeps of TT_als, assuming core index = d
sweep = [d:-1:2, 1:d-1];
tt = tt_0;
for i = 1:maxiter
    for n = 1:2*d-2
        k = sweep(n);
        Tn = contract(tens, tt, k);
        tt.Cores{k} = Tn;
        if n < 2*d-2
            tt = shiftnorm(tt, sweep(n+1));
        else
            tt = shiftnorm(tt,sweep(1));
        end
    end
    if ~isempty(epsilon)
        t_norm = normTens(Tn)^2;
        diff_norm = normTens(Tn-tt_0.Cores{d-1})^2;
        if (tens_norm - t_norm + diff_norm) < epsilon
            return
        end
    end
end
tt.normError = -1;
end

function Tn = contract(tensor, tt, n)
%CONTRACT contracts tensor and tt on all modes except n
%
%INPUT
%   tensor
%   tt
%   n
%OUTPUT
%   Tn : (R_n x I_n x R_n+1)

d = ndims(tt);
ranks = rank(tt);
sz = size(tensor);
leftmodes = prod(sz(1:n-1));    % I_1 I_2 ... I_n-1
rightmodes = prod(sz(n+1:d));   % I_n+1 ... I_N

if n == d
    leftCore = leftcores(tt, n);
    leftCore = leftCore';
    Tn = leftCore * reshape(tensor, leftmodes, sz(n)*rightmodes);
    Tn = reshape(Tn, ranks(n), sz(n), ranks(n+1));

elseif n == 1
    rightCore = rightcores(tt, n);
    rightCore = rightCore';
    Tn = reshape(tensor, leftmodes(n)*sz(n), rightmodes) * rightCore;
    Tn = reshape(Tn, ranks(n), sz(n), ranks(n+1)); % (R_n x I_n x R_n+1)
else
    leftCore = leftcores(tt, n);
    rightCore = rightcores(tt, n);

    leftCore = leftCore';  % ( R_n x I_1 I_2 ... I_n-1)
    rightCore = rightCore';  % (I_n+1 ... I_N x R_n+1)
    
    Tn = leftCore * reshape(tensor, leftmodes, sz(n)*rightmodes); % (R_n x I_n I_n+1 ... I_N)
    Tn = reshape(Tn, ranks(n)*sz(n), rightmodes) * rightCore;   % (R_n I_n x R_n+1)
    
    Tn = reshape(Tn, ranks(n), sz(n), ranks(n+1)); % (R_n x I_n x R_n+1)
end

end

