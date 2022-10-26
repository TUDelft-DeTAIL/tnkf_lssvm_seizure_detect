% function tests = kernel_row_test
% 
% tests = functiontests(localfunctions);
% 
% end
% 
% function test_rows(testCase)
% 
% 
% end

N = 10;
X = rand(N,2);
y = randi([-1 1],N,1);
gamma = 1;
sigma2 = 1;
Omega = (y*y').*kernel_matrix(X, 'RBF_kernel', sigma2) + (1/gamma)*eye(N);

LS = LSSVM(X,y,'RBF_kernel',sigma2,gamma,[]);

kernelMat = zeros(N,N);
for k = 1:N
    kernelMat(k,:) = LS.kernel_row(k);
end
% 
%         XXh = sum(Xtrain.^2,2)*ones(1,nb_data);
%         omega = XXh+XXh'-2*(Xtrain*Xtrain');
%         omega = exp(-omega./(2*kernel_pars(1)));


assert(all(ismembertol(Omega,kernelMat, 0.001,'ByRows',true)))