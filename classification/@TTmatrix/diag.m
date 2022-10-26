function TT = diag(TTm)
%diag(TTm) extracts the elements on the main diagonal of the matrix in
%   TTm-format (TTm), these elements or saved in a TensorTrain (TT).

TT = TensorTrain;
d = ndims(TTm);
sz = size(TTm);
n = sz(:,2);
r = rank(TTm);
TT.Cores = cell(d,1);
TT.Size = sz(:,[1 2 4]);
for k = 1:d
    TT.Cores{k} = zeros(r(k),n(k),r(k+1));
    for j = 1:n(k)
        TT.Cores{k}(:,j,:) = TTm.Cores{k}(:,j,j,:); 
    end
end

end