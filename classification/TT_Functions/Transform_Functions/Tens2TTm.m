function [TTm] = Tens2TTm(tens,ranks, epsilon)
%Tens2TTm(tens, ranks, epsilon) convert a tensor that was reshpae form a matrix into a
%   TTmatrix. Specified tensor must be of dimensions I_1 x J_1 x I_2 x J_2
%   x ... x I_d x J_d , for a matrix of dimensions (I_1 ... I_d) x (J_1 ...
%   J_d).
%
%INPUT
%   tens : specified tensor
%   ranks : max ranks.
%   epsilon : max error
%
%OUTPUT
%   TTm
%   normE

tensSize = size(tens);
rowDims = tensSize(:,1:2:end);
colDims = tensSize(:,2:2:end);
if length(colDims) < length(rowDims)
    colDims = [colDims, 1];
end
if isscalar(rowDims) && isscalar(colDims)
    rowDims = [rowDims 1];
    colDims = [colDims 1];
end
    

d2 = ndims(tens);
d = d2/2;
reshapeVec = rowDims.*colDims;


tensTTformat = reshape(tens,reshapeVec); %contract row and col dims

TT = TT_SVD(tensTTformat,ranks,epsilon);
%% Now reshape cores into TTm format

TTm = TT2TTm(TT,rowDims,colDims);

