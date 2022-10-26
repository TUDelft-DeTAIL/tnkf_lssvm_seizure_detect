function [row] = extractRowTTm(TTm,index)
%extractRowTT(TTm,index) extract the row of the
%   TTmatrix TTm at the index given by index.

d = ndims(TTm);
sizeTens = size(TTm);

% Matrix index convert to Tensor index
[indexRow{1:d}] = ind2sub(sizeTens(:,2)',index);
indexRow = cell2mat(indexRow);

%% Extract
%initialize

row = TensorTrain;
row.Cores = cell(d,1);
row.Size = TTm.Size(:,[1,3,4]);

for k = 1:d
    row.Cores{k} = TTm.Cores{k}(:,indexRow(k),:,:);
    row.Cores{k} = reshape(row.Cores{k}, row.Size(k,:));
end

end