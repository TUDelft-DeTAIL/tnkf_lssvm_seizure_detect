%% Multplication
function C = mtimes(A,B)
%mtimes(A,B) computes the multiplication of A and B. If A and B are both
%   TT's the outerproduct is calculated, the result (C) is thus a TTm. If 
%   either A or B is a scalar, a simple scalar-TT multiplication is
%   computed.

%% scalar multplication
% CHANGE TO MULT AT LOCATION NORM
if isa(A,'TensorTrain') && isscalar(B)
    %% Perform multiplication
    C = A;
    if A.indexNorm == 0
        C.Cores{1} = A.Cores{1}*B;
    else
        C.Cores{A.indexNorm} = A.Cores{A.indexNorm}*B;
    end

elseif isa(B,'TensorTrain') && isscalar(A)
    C = B;
    if B.indexNorm == 0
        C.Cores{1} = B.Cores{1}*A;
    else
        C.Cores{B.indexNorm} = B.Cores{B.indexNorm}*A;
    end
    
elseif isa(A,'TensorTrain') && isa(B,'TensorTrain')
    % to compute the vector outerproduct A*B'
    % --o-- x --o-- becomes   |
    %   |       |           --o--
    %                         |
    C = TT_x_TT(A,B);

else
    error("Multiplication not yet defined for these classes.");
end


end


