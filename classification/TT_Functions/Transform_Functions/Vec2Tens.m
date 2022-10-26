function [tens,d] = Vec2Tens(vec,q)
%Vec2Tens(vec,q) computes the tensorized/quantized version of vec.
%   The parameter q can be either a vector or a scalar. If q is a vector
%   Vec2Tens is equal to reshape(vec,q). When q is a scalar, Vec2Tens tries
%   to compute a d such that q^d = N (N = length(vec)).
%
%INPUT
%   vec : a vector of length N
%   q : quantization parameter
%
%OUTPUT
%   tens : tensorized vector
%   d : dimension of tens


N = length(vec);

if length(q) == 1
    d = log(N)/log(q);
    
    if ~mod(d,1)==0
        error("Cannot quantize vector for this q.");
    end
    
    tsize = q*ones(1,d);
elseif length(q)>=2
    if prod(q) ~= N
        error("Product of elements of q = "+num2str(prod(q))+"must be equal to dimension of the vector = "+ num2str(N));
    end
    tsize = q;
    if nargout >1
        d = length(q);
    end
else
    error("q must be a vector or a scalar");
end

tens = reshape(vec,tsize);

end



