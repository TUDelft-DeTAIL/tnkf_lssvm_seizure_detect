function row = kernel_row(obj, k, varargin)
%KERNEL_ROW(obj, k) or KERNEL_ROW(obj, k, X_test)  calculates the k-th row 
%   of the kernel matrix.
%   For training it calculates yi*yj*Omega(X_train,X_train) + (1/gamma)*I
%   For testing it calculates Omega(X_train, X_test)
%
%INPUT
%   obj : LSSVM object
%   k   : k-th row of the matrix
%   X_test (opt.)   : testing
%OUTPUT
%   row : the row of the kernel matrix


% N = length(y_train);
% row = zeros(1,N);
% 
% for j = 1:N
%     row(1,j) = y_train(k)*y_train(j)*rbf(X_train(j,:), X_train(k,:), sigma2);
% end
% 
% row(1,k) = row(1,k) + 1/gamma;
% end
% 
% 

switch obj.kernel_type
    case 'RBF_kernel'
        sigma2 = obj.kernel_pars;
        if nargin == 2  % kernel matrix for training
% %             diff = obj.X_train - obj.X_train(k,:);
%             diff = pdist2(obj.X_train, obj.X_train(k,:));
% %             row = exp( (-sum(diff.*diff,2)') ./ (2*obj.kernel_pars));
% %             row = row + 1/obj.gamma;
%             diff_norm = diff.^2;    %(vecnorm(diff, 2, 2)')
%             row = obj.y_train(k).*obj.y_train'.*exp(-diff_norm/(2*sigma2));
%             N = length(obj.y_train);
%             row = zeros(1,N);
%             y_k = obj.y_train(k);
%             y_train = obj.y_train;
%             X_train = obj.X_train;
%             X_train_k = X_train(k,:);
%             parfor j = 1:N
%                 row(1,j) = y_k*y_train(j)...
%                             *rbf(X_train(j,:), X_train_k, sigma2);
%             end

%             row = obj.y_train(k).*obj.y_train'.*kernel_matrix( ...
%                 obj.X_train, 'RBF_kernel', sigma2, ...
%                 obj.X_train(k,:))';
% 
%             if obj.Options.weighted && length(obj.gamma) > 2
%                 row(1,k) = row(1,k) + 1/obj.gamma(k);
%             elseif obj.Options.weighted && length(obj.gamma) == 2
%                 if obj.y_train(k) == 1
%                     row(1,k) = row(1,k) + 1/obj.gamma(2);
%                 else    % no seizure
%                     row(1,k) = row(1,k) + 1/obj.gamma(1);
%                 end
%             else
%                 row(1,k) = row(1,k) + 1/obj.gamma;
%             end

        diff = obj.X_train(k,:)-obj.X_train;
        row = (exp( -((sum(diff.*diff,2))'./(2*obj.kernel_pars))) );
%         row = (exp( -((sum(diff.*diff,2))'./(2*obj.kernel_pars))) );
        row(1,k) = row(1,k) + 1/obj.gamma;
        
        elseif nargin == 3      % kernel matrix for testing
            X_test = varargin{1};
            diff = obj.X_train(k,:) - X_test;
            row = exp( (-sum(diff.*diff,2)') ./ (2*obj.kernel_pars));
        end

    otherwise
        error("Kernel " + obj.kernel_type + " not yet implemented.")
end

end

function val = rbf(x,y,sigma2)
    
    z = dot(x,y) - 0.5*vecnorm(x)^2 - 0.5*vecnorm(y)^2;
%     z = - norm(x-y)^2;
    val = exp(z/(2*sigma2));

end




    