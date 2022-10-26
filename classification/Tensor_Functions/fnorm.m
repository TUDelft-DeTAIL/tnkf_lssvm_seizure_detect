function [tensNorm] = fnorm(tens)
%fnorm(tens) computes the Frobenius norm of a given tensor. 

%INPUT 
%   tens : tensor, can be decomposed in TT format.
%OUTPUT
%   tensNorm : Frobenius norm of the tensor

switch class(tens)
    case 'double'
        d = ndims(tens); % d-way tensor
        if d < 3
            tensNorm = norm(tens,'fro');
        else
            tensNorm = normTens(tens);
        end
    case 'TensorTrain'
        tensNorm = normTT(tens);
    otherwise
        error('Input not supported');
end
