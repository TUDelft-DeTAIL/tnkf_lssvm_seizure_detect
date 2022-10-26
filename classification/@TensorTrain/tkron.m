function [C] = tkron(A,B)
%tkron(A,B) computes the kronecker product of two tensor/vectors A and B 
%   represented in TensorTrain format. This is done by stitching the ends of
%   the TensorTrains.
%
%INPUT
%   A : Tensor/vector represented by a d_A dimensional TensorTrain.
%   B : Tensor/vector represented by a d_B dimensional TensorTrain.
%OUTPUT
%   C : Kronecker product of A and B (C = A (x) B) represented by a d_A+d_B 
%       dimensional TensorTrain.

%% Calculate kronecker product

d_A = ndims(A);
d_B = ndims(B);
% set dimension of product
d_C = d_A+d_B;

C = TensorTrain;
C.Size(1:d_B,:) = size(B);
C.Size(d_B+1:d_C,:) = size(A);

% B first due to matlab ordering
for k = 1:d_B
    C.Cores{k} = B.Cores{k};
end
for k = d_B+1:d_C
    C.Cores{k} = A.Cores{k-d_B};    
end

end

