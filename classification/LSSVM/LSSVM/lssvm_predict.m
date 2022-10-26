function [labels, classifier_output] = lssvm_predict(alpha, b, X_train, X_test, y_train, kernel_type, kernel_pars)
%lssvm_predict(..)
%   predict the labels from the provided trained lssvm model

num_test = size(X_test,1);
num_train = size(X_train,1);

if num_train * num_test < 1e6  % only for small datasets
    
    y_train = single(y_train(:));
    K = kernel_matrix(X_train, kernel_type, kernel_pars, X_test);
    
    % K = kernel_matrix(X_train, kernel_type, kernel_pars, X_test);
    classifier_output = K'*(alpha.*y_train) + b;
    labels = sign(classifier_output);
else
    
    % to avoid calling multiple times
    AtY = alpha.*y_train;
    clear alpha y_train

    % set batch size
    N_test = size(X_test,1);
    batchSize = 200;
    iters = 1:batchSize:N_test;
    total_iter = length(iters);

    %  zero initialization
    classifier_output = cell(total_iter,1);
    x_temp = cell(total_iter,1);
 
    % initalize for the parfor loop
    for k = 1:total_iter
        begin_row = iters(k);
        end_row = min([iters(k)+batchSize-1, N_test]); 
        idx_row = begin_row:end_row;
        x_temp{k} = X_test(idx_row,:);
    end
    clear X_test
    
    % par for loop for predictions
    if total_iter > 3

        parfor k = 1:total_iter
          
            K = kernel_matrix(X_train, kernel_type, kernel_pars, ...
            x_temp{k});
            classifier_output{k} = K'*AtY + b;
        end
    else
        for k = 1:total_iter
            K = kernel_matrix(X_train, kernel_type, kernel_pars, ...
            x_temp{k});
            classifier_output{k} = K'*AtY + b;
        end
    end

    % reshape to matrix
    classifier_output = cell2mat(classifier_output);    
    labels = sign(classifier_output);

end