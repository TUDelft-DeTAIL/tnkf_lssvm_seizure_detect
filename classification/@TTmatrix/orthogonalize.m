function [A] = orthogonalize(A,n)
%orthogonalize(A,n) computes the n-orthofonalization of a TT-tensor A.
%
%INPUT
%   A : d-dimensional TTmatrix
%   n : index at which to orthogonalize. All cores 1...n-1 are left
%   orthogonal and all cores n...d are right orthogonal
%OUTPUT
%   A : n-orthogonalized version of TTmatrix A


rowDims = A.Size(:,2);
colDims = A.Size(:,3);

ATT = TTm2TT(A);

ATT = orthogonalize(ATT,n);
A = TT2TTm(ATT,rowDims,colDims);