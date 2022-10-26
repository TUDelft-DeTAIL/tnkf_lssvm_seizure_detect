function [element,indexTT] = extractElementTT(TT,index)
%extractElementTT(TT,index) extract the elments of the TensorTrain or
%   TTmatrix TT at the index given by index.

d = ndims(TT);
sizeTens = size(TT);
r = rank(TT);
switch class(TT)
    case 'TensorTrain'
        sizeTens = sizeTens(:,2)';
        [indexTT{1:d}] = ind2sub(sizeTens,index);
        indexTT = cell2mat(indexTT);
        %% Extract element
        %initialize
        element = 1;
        for k = 1:d
            core_k = reshape(TT.Cores{k}(:,indexTT(k),:),r(k),r(k+1));
            % calculate element by multiplying the cores
            element = element*core_k;
        end
        
        
    case 'TTmatrix'
        % Matrix index convert to Tensor index
        [indexRow{1:d}] = ind2sub(sizeTens(:,2)',index(1));
        [indexCol{1:d}] = ind2sub(sizeTens(:,3)',index(2));
        indexRow = cell2mat(indexRow);
        indexCol = cell2mat(indexCol);
        indexTT = [indexRow',indexCol'];
        %% Extract
        %initialize
        element = 1;

        for k = 1:d
            core_k = reshape(TT.Cores{k}(:,indexTT(k,1),indexTT(k,2),:),r(k),r(k+1));
            % calculate element by multiplying the cores
            element = element*core_k;
        end
        
    otherwise
        error('Unsupported input format, must be a TT or TTm.');
end