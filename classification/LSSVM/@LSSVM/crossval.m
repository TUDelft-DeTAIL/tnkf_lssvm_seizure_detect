function obj = crossval(obj, cv)
%CROSSVAL(LS,cv) on the training set for hyperparameter opt.
%
%INPUT
%   LS  : LSSVM object
%   cv  : cross validation partition object
%
%OUTPUT
%   LS : LSSVM object with results filled in
%

%TODO implement for self-defined validation sets

K = cv.NumTestSets;
% LS = obj;
accuracy = zeros(K,1);
TPR = zeros(K,1);
TNR = zeros(K,1);
F1 = zeros(K,1);

X_train = cell(K,1);
y_train = cell(K,1);
kernel = 'RBF_kernel';
gamma = obj.gamma;
sigma2 = obj.kernel_pars;
opts = obj.Options;
X_test = cell(K,1);
y_test = cell(K,1);

% Predefine validation sets (to enable parallelization)
for k = 1:K
    i_train = training(cv, k);
    i_test = test(cv, k);
    X_train{k} = obj.X_train(i_train,:);
    y_train{k} = obj.y_train(i_train);
    X_test{k} = obj.X_train(i_test,:);
    y_test{k} = obj.y_train(i_test);
end

for k = 1:K
    disp(k)
    LS = LSSVM(X_train{k}, y_train{k}, kernel, gamma, sigma2, opts);
    % Calculate the quantization parametrs for the tensor-trains
    q = factor(length(LS.y_train)+1);
    if max(q) > 20
        warning("Maximum value of q = "+ num2str(max(q))+ ...
            " > 20, please consider quantizing the tensor further, before" + ...
            " computing the tensor-train.")
        [q,Nnew] = getQTTpar(length(LS.y_train)+1);       
        LS.X_train = LS.X_train(1:Nnew-1,:);
        LS.y_train = LS.y_train(1:Nnew-1);
           
        disp(['new q = [' num2str(q(:).') ']']) ;
    end
    LS.Options.kalmanOpt.q = q;   
    % Shuffle the data to alternate
    [LS.X_train, LS.y_train] = alternate_data(LS.X_train, LS.y_train);
    % train the model 
    LS = LS.fit();
    % test the model
    [labels, ~] = LS.predict(X_test{k});
    % evaluate the prediction
    [accuracy(k), TPR(k), TNR(k), F1(k)] = evaluate_results( ...
        y_test{k}, labels);
end
results.accuracy = accuracy;
results.TPR = TPR;
results.TNR = TNR;
results.F1 = F1;

obj.results = results;

end