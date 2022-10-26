function [C] = times(A,B)
%times(A,B) computes the element-wise (Hadamard) product of two
%   tensor-trains A and B.
%
%INPUT
%   A : tensor-train
%   B : tensor-train
%OUTPUT
%   C : C = A.*B, tensor train

if ~isequal(A.Size(:,2),B.Size(:,2))
    error("TT's A and B must be of same size,along 2nd mode")
elseif ~(isa(B,'TensorTrain') && isa(A,'TensorTrain'))
    error("Elementwise multiplication not defined for objects of this class");
end

sz = A.Size;    %size matrix
d = size(sz,1); % dimension of tensors
N =sz(:,2);

C = TensorTrain;
C.Cores = cell(d,1);
C.indexNorm = 0;

for k = 1:d
    Ak = permute(A.Cores{k},[1 3 2]);
    Bk = permute(B.Cores{k},[1 3 2]);
    Ck = zeros(A.Size(k,1)*B.Size(k,1),A.Size(k,3)*B.Size(k,3),N(k));
    for i = 1:N(k)
        Ck(:,:,i) = kron(Ak(:,:,i),Bk(:,:,i));
    end
    C.Cores{k} = permute(Ck,[1 3 2]);
    C.Size(k,:) = size(C.Cores{k},[1 2 3]);
end


