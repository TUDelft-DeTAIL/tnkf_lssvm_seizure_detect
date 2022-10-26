function p = diagP(obj)
%diagP(obj) extract the diagonal of the P-matrix of the KalmanFilter object
%   obj.

if obj.Color
    numLayers = 3;
else
    numLayers = 1;
end
P = obj.P;
sz = P{1}.Size;
lengthP = prod(sz(:,2));

p = zeros(lengthP,numLayers);
for i = 1:numLayers
    pTT = diag(P{i});
    p(:,i) = TT2Vec(pTT);
end

end