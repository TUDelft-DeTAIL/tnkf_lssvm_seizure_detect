function Y = kproduct(tens,mat,k)
%kproduct(tens,mat,k) return the k-mode product of a specified d-way tensor
%   tens.
%INPUT
%   tens : d-way tensor
%   mat : matrix to multiply with tensor
%   k : mode at which to multiply
%OUTPUT
%   Y : k-mode product
%%

sz = size(mat);
if sz(2) >1 && sz(1)>=1
    sizeMat = sz;
    sizeTens = size(tens);
    
    if sizeTens(k)~=sizeMat(2)
        error('Inner tensor dimensions must agree');
    end
    d = ndims(tens);
    sizeY = sizeTens;
    sizeY(k) = sizeMat(1);
    
    perm_order = [k, 1:k-1,k+1,d];
    tens_k = reshape(permute(tens,perm_order),sizeTens(k),[]);
    Y_k = mat*tens_k;
    Y = ipermute(reshape(Y_k,sizeY),perm_order);
    
elseif sz(2) == 1
    vec = mat;
    sizeTens = size(tens);
    
    sizeY = [sizeTens(1:k-1) sizeTens(k+1:end)];
    if isscalar(sizeY)
        sizeY = [sizeY 1];
    end
    % compute mode-k matricization of tens
    tens_k = matricize(tens,k)';
    % perform k-mode product
    Yk = (tens_k*vec)';
    % revert mode-k matricization of product back to tensor
    Y = reshape(Yk,sizeY);%tensorize(Yk,k,sizeY);
end