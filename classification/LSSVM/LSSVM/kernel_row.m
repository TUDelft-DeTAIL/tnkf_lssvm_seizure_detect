function row = kernel_row(X_train, y_train, gam, sigma2, k)
%KERNEL_ROW Compute the k-th row of the kernel matrix
%   Detailed explanation goes here

row = y_train(k).*y_train'.*kernel_matrix( ...
    X_train, 'RBF_kernel', sigma2, ...
    X_train(k,:))';

row(:,k) = row(:,k) + (1/gam)*eye(length(k));
end

