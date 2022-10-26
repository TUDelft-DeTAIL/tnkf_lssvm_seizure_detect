function elems = subsref(A,s)
%SUBSREF Summary of this function goes here
%   Detailed explanation goes here

switch s(1).type
    case '()'
        if length(s(1).subs) == 2
            row_index = s(1).subs{1};
            col_index = s(1).subs{2};
            if strcmp(row_index,':') 
                
                elems = extractColTTm(A,col_index);
                return 
            elseif strcmp(col_index,':') 
                elems = extractRowTTm(A,row_index);
                return
            end

            numRowIndices = length(row_index);
            numColIndices = length(col_index);
            elems = zeros(numRowIndices,numColIndices);
            
            for ii = 1:numRowIndices
                for jj = 1:numColIndices
                    [elems(ii,jj),~] = extractElementTT(A,...
                        [row_index(ii), col_index(jj)]);
                end
            end
        else
            error("Only single index supported.")
        end
    case '{}'
        error('{} indexing not supported');
    case '.'
        elems = builtin('subsref', A, s);  % as per documentation
end
