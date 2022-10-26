function [normA,A] = norm(A)
%norm(A) computes the Frobenius norm of TTmatrix-tensor A. If desired this
%   function also outputs the orthogonalized version of A.
%
%INPUT
%   A : TTmatrix-tensor
%OUTPUT
%   normA : the Frobenius norm of A
%   A : orthogonalized version of A


index = A.indexNorm;
if index ~= 0
    normA = normTens(A.Cores{index});
else
     A = orthogonalize(A,size(A.Size,1));
     normA = normTens(A.Cores{A.indexNorm});
end