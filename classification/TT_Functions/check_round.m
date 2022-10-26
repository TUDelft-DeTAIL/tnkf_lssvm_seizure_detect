function [C] = check_round(A,B,C)
%check_round(A,B,C) checks if C (the product/addition of A and B)
%   needs to be rounded.
%% Check if rounding necessary

if (isa(A,'TensorTrain')||isa(A,'TTmatrix')) && isscalar(B)
    if A.maxRank > 0
        C.maxRank = A.maxRank;
        C.desRank = A.desRank;
        if C.desRank == -1
            C.desRank = C.maxRank;
        end
        if any(rank(C)>C.maxRank)
            C = rounding(C,C.desRank,'r');
        end
    end
elseif (isa(B,'TensorTrain')||isa(B,'TTmatrix')) && isscalar(A)
    if B.maxRank > 0
        C.maxRank = B.maxRank;
        C.desRank = B.desRank;
        if C.desRank == -1
            C.desRank = C.maxRank;
        end
        if any(rank(C)>C.maxRank)
            C = rounding(C,C.desRank,'r');
        end
    end
elseif (isa(A,'TensorTrain')||isa(A,'TTmatrix')) && (isa(B,'TensorTrain')||isa(B,'TTmatrix') )
    
    if A.maxRank > 0 || B.maxRank > 0
        C.maxRank = max(A.maxRank,B.maxRank);
        C.desRank = max(A.desRank,B.desRank);
        if C.desRank == -1
            C.desRank = C.maxRank;
        end
        if any(rank(C)>C.maxRank)
            C = rounding(C,C.desRank,'r');
        end
    end
end

