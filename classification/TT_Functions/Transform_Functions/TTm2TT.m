function [TT,rowDims,colDims] = TTm2TT(TTm)
%TT2TT(TTm) converts a tensor (matrix) that has been
%   represented in the TTmatrix format, into the TT format. The arguments
%   rowDims and colDims are the dimension of the original matrix. 
%
%INPUT:
%   TTm :        Tensor in TensorTrain format (must be of TensorTrain class)
%OUTPUT:
%   TT         Tensor represented in TTmatrix format. 
%   rowDims :   Dimensions of original matrix, the product of the elements 
%               of this vector equals the row dimension of the matrix (I = I_1*I_2*...*I_d).
%   colDims     Column dimensions of the original matrix, product of the
%               elements equal the columns dimension of the matrix (J =
%               J_1*...*J_d).

if ~isa(TTm,'TTmatrix')
    error("In TTm2TT, the first argument must be of class 'TTmatrix'");
end

d = ndims(TTm);


TT = TensorTrain;
TT.Cores = cell(d,1);
rowDims = TTm.Size(:,2);
colDims = TTm.Size(:,3);

TT.Size = [TTm.Size(:,1),rowDims.*colDims,TTm.Size(:,4)];

for k = 1:d
    TT.Cores{k} = reshape(TTm.Cores{k},TT.Size(k,:));
end

TT.indexNorm = TTm.indexNorm;
end

