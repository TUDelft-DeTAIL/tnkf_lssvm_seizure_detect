function [Xr, yr] = alternate_data_sample(X, y, factor0, factor1)
%alternate_data_sample(X, y, factor0, factor1) alternates the training data
%   according to the supplied factors and oversamples the minority class
%
%   factor0 : majority (negative) class
%   factor1 : minority (postive) class

idx_0 = find(y == -1);   % zero/negative class
idx_1 = find(y == 1);   % one/positive class

N = length(y);  % num data_points
Xr = zeros(size(X));
yr = zeros(size(y));
idx_r = zeros(N,1);
n0 = 1;
n1 = 1;
pos = false;    % positive class
count0 = 1;
count1 = 1;


for n = 1:N
    idx_r(n) = idx_0(n0)*(1-pos) + idx_1(n1)*pos;
    if count0 < factor0 && ~pos
        count0 = count0 + 1;
        n0 = n0 + 1;
        pos = false;
    elseif pos && count1 < factor1
        count1 = count1 + 1;
        n1 = n1 + 1;
        pos = true;
    elseif count0 == factor0 && ~pos
        count0 = 1;
        n0 = n0 + 1;
        pos = true;
    elseif count1 == factor1 && pos
        count1 = 1;
        n1 = n1 + 1;
        pos = false;
    end
    if n0 > length(idx_0)
        n0 = 1;
    elseif n1 > length(idx_1)
        n1 = 1;
    end
end     %endfor

Xr = X(idx_r,:);
yr = y(idx_r);

end 