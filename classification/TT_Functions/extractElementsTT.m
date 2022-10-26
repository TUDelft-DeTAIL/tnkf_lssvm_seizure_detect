function [elements,indexTT] = extractElementsTT(TT,index)
%extractElementsTT(TT,index) extract the elments of the TensorTrain or
%   TTmatrix TT at the indices given by index.
%   Vector indices should be represented in a row vector.
%   Matrix indices by a 2 by N matrix, where N is the number of elements to
%   extract.


d = ndims(TT);
switch class(TT)
    case 'TensorTrain'
        numIndices = length(index);
        elements = zeros(numIndices,1);
        indexTT = zeros(numIndices,d);

        for ii = 1:numIndices
            [elements(ii,:),indexTT(ii,:)] = extractElementTT(TT,index(ii,:));
        end

    case 'TTmatrix'
        %% determine all possible combinations of indices
        [A,B] = meshgrid(index(1,:),index(2,:));
        c=cat(2,A',B');
        d=reshape(c,[],2);
        indexRow = d(:,1);
        indexCol = d(:,2);
        
        %% extract indices and place in a matrix
        numRowIndices = length(index(1,:));
        numColIndices = length(index(2,:));
        numIndices = length(indexRow);
        elements = zeros(numRowIndices,numColIndices);
        newRowIndex = rescale(indexRow,1,numRowIndices);
        newColIndex = rescale(indexCol,1,numColIndices);
        
        for ii = 1:numIndices
            elements(newRowIndex(ii),newColIndex(ii)) = extractElementTT(TT,[indexRow(ii),indexCol(ii)]);
        end
        

end