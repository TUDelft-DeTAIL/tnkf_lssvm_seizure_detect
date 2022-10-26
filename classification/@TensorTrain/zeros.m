function TT = zeros(varargin)
%ZEROS Summary of this function goes here
%   Detailed explanation goes here

if nargin == 1
    size_tens = varargin{1};
else
    size_tens = cell2mat(varargin);
end

d = length(size_tens);
TT = TensorTrain;
TT.Size = zeros(d,3);
TT.normError = 0;

for k = 1:d
    TT.Cores{k} = zeros(1, size_tens(k),1);
    TT.Size(k,:) = [1, size_tens(k),1];
end


end

