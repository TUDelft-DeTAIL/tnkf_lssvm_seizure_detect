function [col] = extractColTTm(TTm,index)
%extractElementTT(TTm,index) extract the column of the 
%   TTmatrix TTm at the index given by index.

d = ndims(TTm);
sizeTens = size(TTm);

% Matrix index convert to Tensor index
[indexCol{1:d}] = ind2sub(sizeTens(:,2)',index);
indexCol = cell2mat(indexCol);

%% Extract
%initialize

col = TensorTrain;
col.Cores = cell(d,1);
col.Size = TTm.Size(:,[1,2,4]);

for k = 1:d
    col.Cores{k} = TTm.Cores{k}(:,:,indexCol(k),:);
end

end