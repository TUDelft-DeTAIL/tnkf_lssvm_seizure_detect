function [product] = ttm(tens,mat,modes)
%ttm(tens,mat,k) OR ttm(tens,mat,modes) computes the k-mode tensor-matrix
%   product. If mat is a single matrix the product is computed along mode
%   k. If mat is a cell of matrices consequative k-mode products are
%   computed along the specified modes (i.e. tens x_1 mat{1} x_2 mat{3}).
%INPUT
%   tens : d-way tensor
%   mat : matrix OR cell of matrices
%   modes : mode(s) along with to perform the product
%OUTPUT
%   product : tensor-matrix product

switch class(mat)
    case 'cell'
        N = length(modes);
        if max(size(mat)) ~= N
            error('Number of modes specified does not equal number of matrices')
        elseif min(size(mat)) ~= 1
            error('Cell of matrices have wrong dimensions')
        end
        product = tens;
        for n = 1:N
           product = kproduct(product,mat{n},modes(n)); 
        end
    case 'double'
        product = kproduct(tens,mat,modes);
    otherwise 
        error('Incorrect input type');
end