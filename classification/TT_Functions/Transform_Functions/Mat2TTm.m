function TTm = Mat2TTm(mat,q1,q2,ranks,epsilon)
%Mat2TTm(mat,q1,q2,ranks,epsilon)

tens = Mat2Tens(mat,q1,q2);
TTm = Tens2TTm(tens,ranks,epsilon);


end

