function [c] = dot(A,B)
%dot(A,B) calculates the dot (or inner-) product of tensor-train A and B.
%INPUT
%   A : d-way TensorTrain object.
%   B : d-way TensorTrain object.
%OUTPUT
%   c : dotproduct of A and B (c = <A,B>)

if ~isequal(A.Size(:,2),B.Size(:,2))
    error("TT's A and B must be of same size,along 2nd mode")
end

sz = A.Size;    %size matrix
d = size(sz,1); % dimension of tensors
N =sz(:,2);
rankA = [1; A.Size(:,3)];
rankB = [1; B.Size(:,3)];

c = 1;  % initialize
for k = 1:d
    Z_1 = c*reshape(B.Cores{k},rankB(k),N(k)*rankB(k+1));   % multiply
    Z = reshape(Z_1,rankA(k),N(k),rankB(k+1));  % unfold
    Z_2 = reshape(Z,rankA(k)*N(k),rankB(k+1));  % reshape into matrix
    c = (reshape(A.Cores{k},rankA(k)*N(k),rankA(k+1)))'*Z_2; % contract
end
