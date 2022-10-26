%% Multplication
function C = mtimes(A,B)
%mtimes(A,B) computes the multiplication of A and B. If 
%   either A or B is a scalar, a simple scalar-TT multiplication is
%   computed. If A is a TTm and B a TT, the matrix-vector product is
%   calculated. If A and B are both TTm's the matrix-matrix product is
%   calculated. 
%   Instead of mtimes the * operator can be used.

%% scalar multplication
% CHANGE TO MULT AT LOCATION NORM
if isa(A,'TTmatrix') && isscalar(B)
    C = A;
    if A.indexNorm == 0
        C.Cores{1} = A.Cores{1}*B;
    else
        C.Cores{A.indexNorm} = A.Cores{A.indexNorm}*B;
    end

elseif isa(B,'TTmatrix') && isscalar(A)
    C = B;
    if B.indexNorm == 0
        C.Cores{1} = B.Cores{1}*A;
    else
        C.Cores{B.indexNorm} = B.Cores{B.indexNorm}*A;
    end

elseif isa(A,'TTmatrix') && isa(B,'TensorTrain')
    
    
    C = TTm_x_TT(A,B);
    

elseif isa(A,'TTmatrix') && isa(B,'TTmatrix')
    C = TTm_x_TTm(A,B);

else
    error("Multiplication not yet defined for these classes.");
end

