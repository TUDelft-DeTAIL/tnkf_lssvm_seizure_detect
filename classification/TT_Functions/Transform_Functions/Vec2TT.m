function TT = Vec2TT(vec,q, ranks, epsilon)
%Vec2TT(vec,q,par,opt) converts a vector into a tensor-train.
%
%INPUT
%   vec : vector
%   q : quantization parameter
%   ranks : max ranks
%   epsilon : max error

tens = Vec2Tens(vec,q);
TT = Tens2TT(tens,ranks,epsilon);

end