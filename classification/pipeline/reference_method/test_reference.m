
config;

sets = ["dev", "eval"];
n_sims = 10;

dev_file = strcat(FEATURES_DIR, "dev", '.parquet');
eval_file = strcat(FEATURES_DIR, "eval", '.parquet');

[X_dev, y_dev] = read_data(dev_file);
[X_eval, y_eval] = read_data(eval_file);
if ~isfolder(strcat(FEATURES_DIR,'results/lssvm/'))
    mkdir(strcat(FEATURES_DIR,'results/lssvm/'))
end


parfor k = 1:n_sims
        trained_file = strcat(FEATURES_DIR,'train/lssvm/model_', ...
            num2str(k),'.mat');      
        disp(trained_file)
        F = load(trained_file);
        
        %% DEV
        [predicted_labels, svm_output] = simlssvm(F.model, X_dev);
        
        T = table(predicted_labels, svm_output, y_dev, 'VariableNames', ...
            {'predicted_labels', 'svm_output', 'y_val'});
        
        writetable(T, strcat(FEATURES_DIR, 'results/lssvm/dev',num2str(k), ...
            '_output.csv'))
        
        %% EVAL
        [predicted_labels, svm_output] = simlssvm(F.model, X_eval);
               
        T = table(predicted_labels, svm_output, y_eval, 'VariableNames', ...
            {'predicted_labels', 'svm_output', 'y_val'});
        
        writetable(T, strcat(FEATURES_DIR, 'results/lssvm/eval',num2str(k), ...
            '_output.csv'))

end