function fro_norm = normTens(tens)
%normTens(tens) calculates the Frobenius norm of the tensor tens
%
%INPUT
%   tens : a d-way tensor
%OUTPUT
%   fro_norm : Frobenius norm of the tensor

fro_norm = norm(reshape(tens,numel(tens),1));
end