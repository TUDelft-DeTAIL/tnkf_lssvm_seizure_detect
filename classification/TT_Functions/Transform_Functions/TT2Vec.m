function [vec] = TT2Vec(TT)
%TT2Vec(TT) converts a vector tensor-train back to a vector.

tens = TT2Tens(TT);

vec = reshape(tens,numel(tens),1);
