function [C] = times(A,B)
%times(A,B) computes the element-wise (Hadamard) product of two
%   TTmatrices A and B.
%
%INPUT
%   A : TTmatrix
%   B : TTmatrix
%OUTPUT
%   C : C = A.*B, TTmatrix

rowDims = A.Size(:,2);
colDims = A.Size(:,3);

if any(B.Size(:,2) ~= rowDims) || any(B.Size(:,3) ~= colDims)
    error("Can't multiply two matrices of different size.");
end


A_TT = TTm2TT(A);
B_TT = TTm2TT(B);

C_TT = times(A_TT,B_TT);

C = TT2TTm(C_TT,rowDims,colDims);


