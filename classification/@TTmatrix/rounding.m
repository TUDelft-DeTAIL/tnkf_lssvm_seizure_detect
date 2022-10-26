function [A] = rounding(A, ranks, epsilon)
    %par,opt)
%rounding(A,epsilon,'e') OR rounding(A,rank,'r') performs the TT-rounding 
%   of a given TT A, with prescribed accuracy epsilon or with maximum
%   rank(s).
%
%INPUT
%   A : tensor-train with sub-optimal ranks
%   epsilon/rank : prescribed accuracy epsilon or maximum rank(s).
%   opt : 'e' or 'r' for epsilon or rank resp.
%OUTPUT
%   A : tensor-train with optimal ranks

rowDims = A.Size(:,2);
colDims = A.Size(:,3);

ATT = TTm2TT(A);

ATT = rounding(ATT, ranks, epsilon); %par,opt);

A = TT2TTm(ATT,rowDims,colDims);
