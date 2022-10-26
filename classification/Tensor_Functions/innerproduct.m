function z = innerproduct(X,Y)
%innerproduct(X,Y) computes the innerproduct of two tensor X and Y.
% 
%INPUT: X,Y (two tensors of same size)
%OUTPUT: z, the innerproduct of these two tensors.

% Require tensors to be of same size
if any(size(X)~=size(Y))
    error("Tensors not of same size")
end

dim = numel(X);

X = reshape(X,[1,dim]);
Y = reshape(Y,[1,dim]);

z = dot(X,Y);

end