function [A] = transpose(A)
%transpose(A) computes the transpose of the TTmatrix A. The ' operator can
%   be use instead of transpose(A).
%
%INPUT:
%   A : a TTmatrix object
%OUTPUT
%   At : the transpose of A


d = ndims(A);

for k = 1:d
    A.Cores{k} = permute(A.Cores{k},[1 3 2 4]);
end
A.Size = [A.Size(:,1), A.Size(:,3),A.Size(:,2),A.Size(:,4)];