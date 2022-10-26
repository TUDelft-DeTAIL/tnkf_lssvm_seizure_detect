function [normA,A] = norm(A)
%norm(A) computes the Frobenius norm of TT-tensor A. If desired this
%   function also outputs the orthogonalized version of A.
%
%INPUT
%   A : TT-tensor
%OUTPUT
%   normA : the Frobenius norm of A
%   A : orthogonalized version of A


index = A.indexNorm;
if index ~= 0   % if A is n-orthogonal calculate norm by norm of n-th core 
    normA = normTens(A.Cores{index});   
else %use dot product
    normA = sqrt(dot(A,A));
%     %warning('Using dot function to calculate norm, this may result in slower computation')
%     A = orthogonalize(A,size(A.Size,1));
%     normA = normTens(A.Cores{A.indexNorm});
%     warning("This norm function computes the orthogonalization of the tensor-train, consider orthogonalizing the tensor-train first to avoid unnecessary calculations.")
%     
end