function C = TTm_x_TT(TTm,TT)
%TTm_x_TT(TTm,TT) compute the matrix-vector product of a matrix and a
%   vector in TTmatrix and TensorTrain format. This results in a TT vector.
%
%INPUT
%   TTm : d-dimensional TTmatrix, with dimension I x J
%   TT : d-dimensional TensorTrain with dimensions J 
%OUTPUT
%   C : d-dimensional TensorTrain with dimension I

colDims = TTm.Size(:,2);

if any(colDims ~= TT.Size(:,2))
    error("Dimensions do not match.");
end

d = ndims(TT);
C = TensorTrain;
C.Cores = cell(d,1);
C.Size = [TTm.Size(:,1).*TT.Size(:,1),TTm.Size(:,2),TTm.Size(:,4).*TT.Size(:,3)];
Cores = cell(d,1);

for k = 1:d
    %% First permute the TTm and TT 
    TTm_p = permute(TTm.Cores{k},[1 2 4 3]);    % set J_k as last dim
    TT_p = permute(TT.Cores{k},[2 1 3]);        % set J_k as first dim
    
    %% Reshape into matrices to perform multiplication
    TTm_r = reshape(TTm_p,TTm.Size(k,1)*TTm.Size(k,2)*TTm.Size(k,4),TTm.Size(k,3));
    TT_r = reshape(TT_p,TT.Size(k,2),TT.Size(k,1)*TT.Size(k,3));
    
    %% Compute contraction and reshape it
    contr = TTm_r*TT_r;
    
    contr_r = reshape(contr,TTm.Size(k,1),TTm.Size(k,2),TTm.Size(k,4),TT.Size(k,1),TT.Size(k,3)); % unfold
    contr_p = permute(contr_r,[1 4 2 3 5]); % permute dimensions to P_(k-1) x R_(k-1) x I_k x P_k x R_k
    
    % save cores
    Cores{k} = reshape(contr_p,C.Size(k,1:3)); % reshape to P_(k-1) R_(k-1) x I_k x P_k R_k
  
end
C.Cores = Cores;

end