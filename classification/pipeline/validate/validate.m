function validate(VALIDATION_FEATURES, TRAINED_MODEL, TRAINING_FILE, RESULTS_DIR)
    %validate(VALIDATION_FEATURES, TRAINED_MODEL,
    %TRAINING_FILE,RESULTS_DIR)
disp("loading training data...")
T = matfile(TRAINING_FILE)
%% Load validation data and trained model
disp("loading validation data...")
[X_val, y_val] = read_data(VALIDATION_FEATURES);

disp("loading trained model...")
LS = load(TRAINED_MODEL);
LS = LS.LS;

if isempty(LS.X_train)
    LS.X_train = single(T.X_train);
    LS.y_train = single(T.y_train);
end

%% NORMALIZE  
X_val = (X_val- T.meanX)./T.stdX;

%% PREDICT
disp("Predict labels...")
[predicted_labels, svm_output] = LS.predict(X_val); % no TT in prediction just yet
var_output = -1;
%% Results folder of current parameters
disp("Saving results...")
results_dirname = strcat(RESULTS_DIR,"gamma="+num2str(LS.gamma,'%.2f'), ...
    "_sigma2=",num2str(LS.kernel_pars,'%.2f'),"/")
if ~exist(results_dirname, 'dir')
    mkdir(results_dirname)
end
save(strcat(results_dirname,'predicted.mat'), 'svm_output', ...
    'predicted_labels', 'var_output', '-v7.3')

%% EVALUATE RESULTS
disp("")
[Accuracy, TPR, TNR,F1] = evaluate_results(y_val, predicted_labels);
[x_curve, y_curve, ~, auc] = perfcurve(y_val, svm_output, 1, 'XCrit', ...
    'prec', 'YCrit', 'reca');

%% PLOT RESULTS
f = figure('visible','off');
plot(x_curve,y_curve,'b-')
xlabel('precision')
ylabel('recall')
title( strcat("Precision-Recall Curve (auc = ",num2str(auc),")"));
saveas(f, results_dirname +'curve','fig')

fileID = fopen(strcat(results_dirname , 'out.txt'), 'w')
fprintf(fileID, ['Accuracy = %.3f\n TPR = %.3f\n TNR = %.3f\n F1 = %.3f\n ' ...
    'AUC = %.3f'], ...
        [Accuracy, TPR, TNR, F1, auc])
fclose(fileID)

end
