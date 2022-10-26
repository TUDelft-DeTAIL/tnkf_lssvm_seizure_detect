function C = TTm_x_TTm(A,B)
%TTm_x_TTm(A,B) computes the matrix-matrix product of two matrix A and B
%   decomposed into the TTmatrix format. 
%
%INPUT
%   A : TTmatrix of dimensions I x J (I = I1 x ... x Id, etc)
%   B : TTmatrix of dimensions J x M
%OUTPUT
%   C : TTmatrix of dimension I x M


if any(A.Size(:,3) ~= B.Size(:,2))
    error("Dimensions do not match, column dimension first matrix must equal row dimension of second.");
end

d = ndims(A);
C = TTmatrix;
C.Cores = cell(d,1);
C.Size = [A.Size(:,1).*B.Size(:,1),A.Size(:,2),B.Size(:,3),A.Size(:,4).*B.Size(:,4)];
Cores = cell(d,1);

for k = 1:d
    %% First permute the TTm and TT 
    A_p = permute(A.Cores{k},[1 2 4 3]);    % set J_k as last dim
    B_p = permute(B.Cores{k},[2 1 3 4]);        % set J_k as first dim
    
    %% Reshape into matrices to perform multiplication
    A_r = reshape(A_p,A.Size(k,1)*A.Size(k,2)*A.Size(k,4),A.Size(k,3));
    B_r = reshape(B_p,B.Size(k,2),B.Size(k,1)*B.Size(k,3)*B.Size(k,4));
    
    %% Compute contraction and reshape it
    contr = A_r*B_r;
    
    contr_r = reshape(contr,A.Size(k,1),A.Size(k,2),A.Size(k,4),B.Size(k,1),B.Size(k,3),B.Size(k,4)); % unfold
    contr_p = permute(contr_r,[1 4 2 5 3 6]); % permute dimensions to P_(k-1) x R_(k-1) x I_k x P_k x R_k
    
    %% save cores
    Cores{k} = reshape(contr_p,C.Size(k,:)); % reshape to P_(k-1) R_(k-1) x I_k x P_k R_k
  
end
C.Cores = Cores;
    

end