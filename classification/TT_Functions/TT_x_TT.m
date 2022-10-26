function [C] = TT_x_TT(A,B)
%TT_x_TT(A,B) computes the outerproduct of two (vector) TensorTrains. This
%   results in a TTmatrix C. A and B must be two vector TT's of same
%   dimensions.
%
%INPUT
%   A : d-dimensional TensorTrain
%   B : d-dimensional TensorTrain
%OUTPUT
%   C : d-dimensional TTmatrix, that is the outerproduct of A and B.


d = ndims(A);

if d~=ndims(B)
    error("Dimensions of TT's not equal")
end

C = TTmatrix;
C.Size = [A.Size(:,1).*B.Size(:,1),A.Size(:,2),B.Size(:,2),A.Size(:,3).*B.Size(:,3)];
C.Cores = cell(d,1);
cores = cell(d,1);

for k = 1:d
    %% Reshape into vectors
    A_r = reshape(A.Cores{k},A.Size(k,1)*A.Size(k,2)*A.Size(k,3),1);
    B_r = reshape(B.Cores{k},1,B.Size(k,1)*B.Size(k,2)*B.Size(k,3));
    %% Permorm core multiplication
    mult = A_r*B_r;
    %% Reshape and permute dimensions
    mult_r = reshape(mult,A.Size(k,1),A.Size(k,2),A.Size(k,3),B.Size(k,1),B.Size(k,2),B.Size(k,3));
    mult_p = permute(mult_r,[1 4 2 5 3 6]);
    %% Save cores
    cores{k} = reshape(mult_p,C.Size(k,:));
end
C.Cores = cores;


end