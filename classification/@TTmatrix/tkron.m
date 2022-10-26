function [C] = tkron(A,B)
%tkron(A,B) computes the kronecker product of two matrices A and B 
%   represented in TTmatrix format. This is done by stitching the ends of
%   the TTm's.
%
%INPUT
%   A : Matrix represented by a d_A dimensional TTmatrix.
%   B : Matrix represented by a d_B dimensional TTmatrix.
%OUTPUT
%   C : Kronecker product of A and B (C = A (x) B) represented by a d_A+d_B 
%       dimensional TTmatrix.

%% Calculate
%

d_A = ndims(A);
d_B = ndims(B);

d_tot = d_A+d_B;

C = TTmatrix;
C.Size(1:d_B,:) = size(B);
C.Size(d_B+1:d_tot,:) = size(A);

% B first due to matlab ordering
for k = 1:d_B
    C.Cores{k} = B.Cores{k};
end
for k = d_B+1:d_tot
    C.Cores{k} = A.Cores{k-d_B};    
end


end

