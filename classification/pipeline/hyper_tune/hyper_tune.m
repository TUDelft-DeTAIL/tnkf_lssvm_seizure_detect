%% TUNE HYPERPARAMETER ON SMALLER SUBSETS OF THE TRAINING SET

function  hyper_tune(hyper_folder, grid_param, iter)
%% Load data to memory
% test:

confidence = zeros(10,1);
acc = zeros(10,1);
auc_roc = zeros(10,1);
f1 = zeros(10,1);
tpr = zeros(10,1);
tnr = zeros(10,1);
auc_prec = zeros(10,1);
disp(hyper_folder)

for i = 1:10
    disp("Loading Training Data...")
    
    fold = strcat(hyper_folder,'fold_',num2str(i-1),'/');
    % load training data
    [X_train, y_train] = read_data(strcat(fold,'train.parquet'));
    X_train = single(X_train);
    y_train = single(y_train);
    g = load(grid_param);
    
    Ntot = prod(g.optsLSSVM.kalmanOpt.q);
    X_train = X_train(1:Ntot-1,:);
    y_train = y_train(1:Ntot-1,:);
    
    disp("Alternating data...")
    [X_train, y_train] = alternate_data(X_train, y_train);
    
    %% Start Training
    % Initialize LSSVM object
    LS = LSSVM(X_train, y_train, "RBF_kernel", g.grid.sigma2(iter), ...
        g.grid.gamma(iter), g.optsLSSVM, []);
    %% Train (and time)
    disp("Training data...")
    tic;
    LS = LS.fit();
    toc;
    
    %% Load test set
    disp("Loading test data...")
    [X_test, y_test] = read_data(strcat(fold, 'test.parquet'));
    X_test = single(X_test);
    y_test = single(y_test);
    
    %% Evaluate results
    [labels, classifier_output] = LS.predict(X_test);
    
    %% Calculate confidence
    if exist("variance_output",'var')
        variance_output = abs(variance_output);
        upperbound = classifier_output + 2*sqrt(variance_output);
        lowerbound = classifier_output - 2*sqrt(variance_output);
        upp_label = sign(upperbound);
        low_label = sign(lowerbound);
        sumbounds = sum((upp_label~=labels)+(low_label~=labels));
        confidence(i) = 1- sumbounds/length(classifier_output);
    else 
        confidence(i) = nan;
    end
    
    %% Other results
    [acc(i), tpr(i), tnr(i), f1(i)] = evaluate_results(y_test, labels);
    [~, ~, ~, auc_prec(i)] = perfcurve(y_test, classifier_output, 1, 'XCrit', 'prec', 'YCrit', 'reca');
    [~, ~, ~, auc_roc(i)] = perfcurve(y_test, classifier_output, 1);
end

%% write out

fileID = fopen(strcat(hyper_folder,'results',num2str(iter),'.txt'), 'w');
fprintf(fileID, 'Kernel parameters \n');
fprintf(fileID, 'sigma2 = %.3f, gamma = %.3f \n', g.grid.sigma2(iter), g.grid.gamma(iter));
fprintf(fileID,"\n");
fprintf(fileID,"Results: (min, max, mean) \n");
fprintf(fileID,"2 sigma confidence = %.2f, %.2f, %.2f\n", min(confidence), max(confidence), mean(confidence));
fprintf(fileID,"Accuracy = %.3f, %.3f, %.3f\n", min(acc), max(acc), mean(acc));
fprintf(fileID,"TPR = %.3f, %.3f, %.3f\n", min(tpr), max(tpr), mean(tpr));
fprintf(fileID, "TNR = %.3f, %.3f, %.3f\n", min(tnr), max(tnr), mean(tnr));
fprintf(fileID, "F1 = %.3f, %.3f, %.3f\n", min(f1), max(f1), mean(f1));
fprintf(fileID, "AUC of precision-recall = %.3f, %.3f, %.3f\n", min(auc_prec), max(auc_prec), mean(auc_prec));
fprintf(fileID, "AUC of ROC = %.3f, %.3f, %.3f\n", min(auc_roc), max(auc_roc), mean(auc_roc));
fclose(fileID);


end