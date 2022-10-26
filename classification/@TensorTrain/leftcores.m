function tens = leftcores(TT,n)
%LEFTCORES contract the cores to the left of mode n
%
%INPUT
%   tt : tensor-train
%   n : mode at which to stop contraction
%OUTPUT
%   cores : contracted cores (I_1 I_2 ... I_n-1 x R_n)

if n ==1
    tens = 1;
    return
end
% sz = size(tt);
% sz = sz(:,2);
% ranks = rank(tt);
% 
% cores = reshape(tt.Cores{1}, sz(1), ranks(2));
% N_tot = 1;
% for i = 2:n-1
%     core_i = reshape(tt.Cores{i}, ranks(i), ranks(i+1)*sz(i));
%     cores = cores * core_i;
% %     N_tot = N_tot * sz(i-1);
%     cores = reshape(cores, [], ranks(i+1));
% end
% % cores = cores';
% end

G = TT.Cores;   % TT cores
sizeMat = TT.Size;  % size matrix of the cores

d = size(sizeMat,1);    % tens is a d-way tensor

% initialize tens with 1st core, reshape into a matrix
tens = reshape(G{1},sizeMat(1,2),sizeMat(1,3)); 

% 
N_tot = 1;
for k = 1:n-2
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