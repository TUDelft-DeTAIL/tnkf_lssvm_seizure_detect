function TTm = eye(varargin)
%EYE Summary of this function goes here
%   Detailed explanation goes here

if nargin == 1
    size_tens = varargin{1};
else
    size_tens = cell2mat(varargin);
end

d = length(size_tens);
TTm = TTmatrix;

for k = 1:d
    TTm.Cores{k} = reshape(eye(size_tens(k)), ...
        [1, size_tens(k), size_tens(k), 1]);
    TTm.Size(k,:) = [1, size_tens(k), size_tens(k),1];
end
TTm.normError = 0;
end

