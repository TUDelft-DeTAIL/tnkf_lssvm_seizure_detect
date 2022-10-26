function A = tensorize(An,n,sizeA)
%tensorize(An,n,sizeA): revert mode-n matricization (An) of tensor A back  
%   to its original tensor format.
%
%INPUT
%   An      : mode-n matricization of A
%   n       : mode along which A was matricized
%   sizeA   : original size of A
%OUTPUT
%   A : original tensor A

ndim = length(sizeA);    % number of dimensions A

tempsize = [sizeA(n), sizeA(1:n-1),sizeA(n+1:ndim)];

A = ipermute(reshape(An,tempsize),[n, 1:n-1, n+1:ndim]);
end
