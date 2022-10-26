%% Substraction
function C = minus(A,B)
%minus(A,B) substracts TensorTrain A with TensorTrain B. 
%INPUT
%   A : d-way TensorTrain object
%   B : d-way TensorTrain object
%OUTPUT
%   C : A-B


if isa(B,'TensorTrain') && isa(A,'TensorTrain')
    C = A+ (-1)*B;
else
    error("Substraction not defined for objects of this class");
end
