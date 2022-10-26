function [Xr, yr] = alternate_data(X, y)
%alternate_data(X, y) alternates the training data
%   such that the different classes are shuffled.

idx_0 = find(y == -1);   % zero/negative class
idx_1 = find(y == 1);   % one/positive class

if length(idx_0) == length(idx_1)
    idx = [idx_0; idx_1];
    idx = idx(:);
    Xr = X(idx,:);
    yr = y(idx);
    return
else
    idx = cat(1, idx_0(:), idx_1(:));
    idx([1:2:end,2:2:end]) = idx;
    Xr = X(idx,:);
    yr = y(idx);
end

% factor0 = 1;
% factor1 = 1;
% 
% N = length(y);  % num data_points
% n0 = 1;
% n1 = 1;
% pos = false;    % positive class
% count0 = 1;
% count1 = 1;
% idx_r = zeros(N,1);
% 
% for n = 1:N
%     idx_r(n) = idx_0(n0)*(1-pos) + idx_1(n1)*pos;
%     if count0 < factor0 && ~pos
%         count0 = count0 + 1;
%         n0 = n0 + 1;
%         pos = false;
%     elseif pos && count1 < factor1
%         count1 = count1 + 1;
%         n1 = n1 + 1;
%         pos = true;
%     elseif count0 == factor0 && ~pos
%         count0 = 1;
%         n0 = n0 + 1;
%         pos = true;
%     elseif count1 == factor1 && pos
%         count1 = 1;
%         n1 = n1 + 1;
%         pos = false;
%     end
%     if n0 > length(idx_0)
%         n0 = 1;
%     elseif n1 > length(idx_1)
%         n1 = 1;
%     end
% end     %endfor
% 
% Xr = X(idx_r,:);
% yr = y(idx_r);

end 