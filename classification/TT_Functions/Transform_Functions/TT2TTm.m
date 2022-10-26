function [TTm] = TT2TTm(TT,rowDims,colDims)
%TT2TTm(TT,rowDims,colDims) converts a tensor (matrix) that has been
%   represented in the TT format, into the TT_matrix format. The arguments
%   rowDims and colDims are the dimension of the original matrix. 
%
%INPUT:
%   TT :        Tensor in TensorTrain format (must be of TensorTrain class)
%   rowDims :   Dimensions of original matrix, the product of the elements 
%               of this vector equals the row dimension of the matrix (I = I_1*I_2*...*I_d).
%   colDims     Column dimensions of the original matrix, product of the
%               elements equal the columns dimension of the matrix (J =
%               J_1*...*J_d).
%OUTPUT:
%   TTm         Tensor represented in TTmatrix format. 

if ~isa(TT,'TensorTrain')
    error("In TT2TTm, the first argument must be of class 'TensorTrain'");
end

d = ndims(TT);

if (length(rowDims) ~= d) || (length(colDims) ~= d)
    error("Specified matrix dimension must be equal in length to the dimnesion of the tensor.")
elseif isrow(rowDims) && isrow(colDims)
    rowDims = rowDims';
    colDims = colDims';
end

TTm = TTmatrix;
TTm.Size = [TT.Size(:,1),rowDims,colDims,TT.Size(:,3)];

% For parallel for loop
TTcores = TT.Cores;
cores = cell(d,1);
size1 = TT.Size(:,1);
size2 = rowDims;
size3 = colDims;
size4 = TT.Size(:,3);

for k = 1:d
    cores{k} = reshape(TTcores{k},size1(k),size2(k),size3(k),size4(k));%TTm.Size(k,:));
end

TTm.Cores = cores;

TTm.indexNorm = TT.indexNorm;
TTm.normError = TT.normError;
end

