function [tens,rowDims,colDims] = Mat2Tens(mat,q1,q2)
%Mat2Tens(mat,q1,q2) computes the tensorized/quantized version of mat. 
%   The parameter q can be either a vector or a scalar. If q is a vector 
%   Vec2Tens is equal to reshape(vec,q). When q is a scalar, Vec2Tens tries
%   to compute a d such that q^d = N (N = length(vec)). 
%
%INPUT
%   mat : a matrix of size N x M
%   q1 : quantization parameter for row indices
%   q2 : quantization parameter for col indices
%
%OUTPUT
%   tens : tensorized vector
%   d : dimension of tens

sz = size(mat);

if length(q1)>1 && length(q2)>1
    rowDims = q1;
    colDims = q2;
    d1 = length(q1);
    d2 = length(q2);
    if prod(rowDims) ~= sz(1) || prod(colDims) ~= sz(2)
        error("Product of quantization vector does not equal size of matrix.");
    end
elseif length(q1)==1 && length(q2)==1
    sz = size(mat);
    if sz(1,1) == 1 
        warning("Input is not a matrix but a vector, using Vec2Tens");
        [tens,d] = Vec2Tens(mat,q2);
        rowDims = ones(1,d);
        colDims = q2*ones(1,d);
        return
    elseif sz(1,2)==1
        warning("Input is not a matrix but a vector, using Vec2Tens");
        [tens,d] = Vec2Tens(mat,q1);
        rowDims = q1*ones(1,d);
        colDims = ones(1,d);
        return
    else 
        d1 = log(sz(1,1))/log(q1);
        d2 = log(sz(1,2))/log(q2);
    end
    if ~mod(d1,1)==0 || ~mod(d2,1)==0
       error("Cannot quantize matrix for these q's."); 
    end

    rowDims = q1*ones(1,d1);
    colDims = q2*ones(1,d2);
else
    error("Unsupported input format.");
end

%% Add ones if d1>d2 or d1<d2
d_diff = d1-d2;
if d_diff>0
    colDims = [colDims,ones(1,d_diff)];
    d2 = d2+d_diff;
elseif d_diff<0
    rowDims = [rowDims,ones(1,-d_diff)];
    d1 = d1-d_diff;
end

d = d1+d2;
%% Permute the dimensions 
%   I_1 x...x I_d x J_1 x...x J_d --> I_1 x J_1 x...x I_d x J_d
permuteDims = zeros(1,d);
index_odd = 1:2:d-1;
index_even = 2:2:d;

permuteDims(index_odd) = 1:d1;
permuteDims(index_even) = (d1+1):d;

tens = permute(reshape(mat,[rowDims,colDims]),permuteDims);


end