function [TT] = TT_SVD(A, ranks, epsilon)
%par,option,varargin)
%TT_SVD(A,epsilon,'e') or TT_SVD(A,ranks,'r') returns the tensor-train
%   decomposition of a given tensor A.
%
%INPUT
%   A : d-dimensional tensor
%   epsilon (accuracy) OR ranks (vector with TT-ranks or scalar with max_rank)
%   option : char, 'e' for prescribed accuracy, 'r' for prescribed
%   maximal rank
%OUTPUT
%   TT : TensorTrain object

%%

% switch option
%     case 'e'
%         
%         TT = TT_SVD_eps(A,par);
%         
%     case 'r'
%         
%         TT = TT_SVD_rank(A,par);
%         
%     otherwise
%         error("Option specified must be 'e' or 'r'.");
% end
% if nargin == 4
%     TT.maxRank = varargin{1};
% end

TT = TT_SVD_new(A, ranks, epsilon);