function [mat,q1,q2] = TTm2Mat(TTm)
%TTm2Mat(TTm) converts a tensor-train matrix back to a matrix
%representation. 
%
%INPUT:
%   TTm : a tensor-train matrix
%OUTPUT:
%   mat : original matrix
%   q1 : quantization parameter rows
%   q2 : quantization parameter columns

d = ndims(TTm);
if nargout > 1
    q1 = TTm.Size(:,2)';
    q2 = TTm.Size(:,3)';
end
%% First convert to TT
[TT,rowDims,colDims] = TTm2TT(TTm);
% extract original matrix dimensions
m = prod(rowDims);
n = prod(colDims);

%% Convert TT to tensor
tens = TT2Tens(TT);

%% Convert tensor to matrix
dimVector = zeros(1,2*d);   % set size
index_odd = 1:2:(2*d-1);    % odd indices till 2d-1
index_even = 2:2:2*d;       % even indices till 2d
dimVector(index_odd) = rowDims; % place rows at odd indices
dimVector(index_even) = colDims;    % place columns at even indices

% reshape tensor such that row and column indices are separated
tens_r = reshape(tens,dimVector);

% permute the indices such that first the rows and then the column
% dimensions
tens_p = permute(tens_r,[index_odd, index_even]);

% final reshape to original dimension
mat = reshape(tens_p,m,n);
