function TT = Tens2TT(tens,ranks, epsilon)
%Tens2TT(tens,ranks, epsilon) transforms a tensor into a tensor-train. This 
%   function is the same as TT_SVD.

TT = TT_SVD(tens,ranks,epsilon);



end