function elems = subsref(A,s)
%SUBSREF Summary of this function goes here
%   Detailed explanation goes here

switch s(1).type
    case '()'
        if length(s(1).subs) == 1
            index = s(1).subs{1};
            numIndices = length(index);
            elems = zeros(numIndices,1);
            
            for ii = 1:numIndices
                [elems(ii,:),~] = extractElementTT(A,index(ii));
            end
        else
            error("Only single index supported.")
        end
    case '{}'
        error('{} indexing not supported');
    case '.'
        elems = builtin('subsref', A, s);  % as per documentation
end
