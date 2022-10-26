function [An,sizeA]= matricize(A,n)
%matricise(A,n) returns the mode-n matricization of a d-dimensional tensor
%   A.
%INPUT
%   A : d-dimensional tensor
%   n : mode at which the tensor is matricized
%OUTPUT
%   An : mode-n matricization of A
%   sizeA : (optional) return size of original tensor


ndim = ndims(A);    % number of dimensions A
rdim = size(A,n); % number of rows of An

% matricize A along dimension n
An = reshape(permute(A,[n, 1:n-1, n+1:ndim]),rdim,[]);

% also return original size of A (in case of 'refolding')
if nargout > 1
    sizeA = size(A);
end