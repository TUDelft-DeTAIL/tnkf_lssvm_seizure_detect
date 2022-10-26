function tens = rightcores(TT,n)
%RIGHTCORES contract the cores to the right of mode n
%
%INPUT
%   tt : tensor-train
%   n : mode at which to stop contraction
%OUTPUT
%   cores : contracted cores (R_n+1 x I_n+1 ... I_N)

N = ndims(TT);
if n ==N
    tens = 1;
    return
end
% sz = size(tt);
% sz = sz(:,2);
% ranks = rank(tt);
% 
% cores = reshape(tt.Cores{N}, ranks(N), sz(N));
% N_tot = sz(N);
% for i = N-1:-1:n+1
%     core_i = reshape(tt.Cores{i}, ranks(i)*sz(i), ranks(i+1));
%     temp = core_i * cores;
%     cores = reshape(temp, ranks(i), N_tot*sz(i));
%     N_tot = N_tot*sz(i);
% end


G = TT.Cores;   % TT cores
sizeMat = TT.Size;  % size matrix of the cores

d = size(sizeMat,1);    % tens is a d-way tensor

if n == N-1
    tens = reshape(G{n+1},sizeMat(n+1,1), sizeMat(n+1,2)*sizeMat(n+1,3) );
    return
end


% initialize tens with (n+1)-th core, reshape into a matrix
tens = reshape(G{n+1},sizeMat(n+1,1)*sizeMat(n+1,2),sizeMat(n+1,3)); 


% 
N_tot = sizeMat(n+1,1); %sizeMat(n+1,2);
for k = n+1:d-2
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
tens = reshape(tens, sizeMat(n+1,1), prod(sizeMat(n+1:end,2)));



end