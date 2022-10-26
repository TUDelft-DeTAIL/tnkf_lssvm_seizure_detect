function [tens] = TT2Tens(TT)
%TT2Tens(TT) converts a tensor that is decomposed in the tensor-train
%   (TT) format back to its original tensor format.
%
%INPUT:
%   TT: tensor in the TT format with d cores, struct with elements 
%   TT.Cores, TT.Size
%OUTPUT:
%   tens: d-way tensor

G = TT.Cores;   % TT cores
sizeMat = TT.Size;  % size matrix of the cores

d = size(sizeMat,1);    % tens is a d-way tensor

% initialize tens with 1st core, reshape into a matrix
tens = reshape(G{1},sizeMat(1,2),sizeMat(1,3)); 
% 
N_tot = 1;
for k = 1:d-2
    % reshape (k+1)th core into matrix by merging the second and third
    % dimension
    temp = reshape(G{k+1},sizeMat(k+1,1),sizeMat(k+1,2)*sizeMat(k+1,3)); 
    % multiply k-th and (k+1)-th core such that    o--o-- becomes o--
    %                                              |              |
    mult = tens*temp;
    % calculate new dimension N_tot = N_1*...*N_{k+1}
    N_tot = N_tot *sizeMat(k,2);
    % unfold the matrix into a 3-D tensor of size (N_tot,N_{k+1},R_{k+2})
    % o-- --> --o--
    % |         |
%     unfold = reshape(mult,N_tot,sizeMat(k+1,2),sizeMat(k+1,3));
    % reshape into tensor of size (N_tot*N_{k+1},R_{k+2}) --o-- 
    tens = reshape(mult,N_tot*sizeMat(k+1,2),sizeMat(k+1,3));
end
tens = tens*G{d};
tens = reshape(tens,sizeMat(:,2)');
