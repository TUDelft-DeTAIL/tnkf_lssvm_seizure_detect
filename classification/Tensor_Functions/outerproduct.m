function X = outerproduct(varargin)
% Input: vectors a1, a2, ... an.
% Output: X, the outer product of a1 o a2 o ... o aN
%
% Write a Matlab function that efficiently computes the outer product of any given number of arbitrary
% vectors.
% Now use your function to compute the outer product A1=a o b o c (the circle o stands for the outer
% product) of three random vectors a,b,c with dimensions(=lengths) 4,2,3 respectively. Then compute
% the other product A2=b o a o c. Are these two tensors identical or different? Can you write Matlab
% code to transform the second tensor A2 into A1?
% % 

%% 
if nargin == 0
    X = [];
    return
elseif nargin == 1
    X = varargin;
    return
end

% Initialize X to be a column vector
if size(varargin{1},1)<size(varargin{1},2)
    X = varargin{1}';
else
    X = varargin{1};
end

% perform outerproduct
for k = 2:nargin
    b = reshape(varargin{k},[ones(1,k-1) length(varargin{k})]);
    X =  X.*b;
end

end