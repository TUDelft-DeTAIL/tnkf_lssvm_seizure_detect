%% TUNE HYPERPARAMETER ON SMALLER SUBSET OF THE TRAINING SET
clearvars
config;

%% Set kalman parameters
opts = struct;
%rank
opts.Rank.C = 30;
opts.Rank.P = 1;
opts.Rank.x = 30;
opts.Rank.s = inf;
opts.Rank.K = 6;
% eps
opts.Eps.x = 0;
opts.Eps.P = 0;
opts.Eps.K = 0;
opts.Eps.s = 0.001;
opts.Eps.C = 0;
% other param
opts.R = 0;
opts.lambda = 1;
opts.p0 = 1;
opts.x0 = "zero";


%% Options LSSVM
optsLSSVM = struct;
optsLSSVM.weighted = false;
optsLSSVM.method = "kalmanTT";
optsLSSVM.kalmanOpt = opts;

%% Kernel parameters
% Kernel parameters
sigma2 = 12; %grid_matrix(1,I_grid);
gamma = 0.1; %grid_matrix(2,I_grid);

%%

datafolder = strcat(FEATURES_DIR, "train/lssvm/");
temp_files = dir(strcat(datafolder, "data*"));
% files = zeros(length(temp_files),1);
for i = 1:length(temp_files)
    files(i) = strcat(datafolder, temp_files(i).name);
end
N_files = length(files);

%% Load data to memory
acc = zeros(N_files,1);
auc_roc = zeros(N_files,1);
f1 = zeros(N_files,1);
tpr = zeros(N_files,1);
tnr = zeros(N_files,1);
auc_prec = zeros(N_files,1);
results_folder = strcat(FEATURES_DIR, "results/tnkf_subset/");
if ~isfolder(results_folder)
    mkdir(results_folder)
end
%  = cell(N_files, 1);

for i = 1:N_files
    %% Load file
    data = load(files(i));
    %% Set training data 
    X_train = single(data.X_train);
    y_train = single(data.y_train);
    N_train = length(y_train);
    X_train = X_train(1:end-1,:);
    y_train = y_train(1:end-1);
    % alternate
    [X_train, y_train] = alternate_data(X_train, y_train);
    % normalize
    meanX = mean(X_train);
    stdX = std(X_train);
    X_train = (X_train - meanX)./stdX;

    %% Start Training
    disp(i)
    optsLSSVM.kalmanOpt.q = factor(N_train);
    % Initialize LSSVM object
    LS = LSSVM(X_train, y_train, "RBF_kernel", sigma2, ...
        gamma, optsLSSVM, []);
    %% Train (and time)
    disp("Training data...")
    tic;
    LS = LS.fit();
    toc;
    %% Save trained model
    disp("Saving trained model...")
    save(strcat(datafolder, "tnkf_", num2str(i)), "LS", "meanX", "stdX")
    
    %% Load dev set
    SET = 'dev';
    val_file = strcat(FEATURES_DIR, SET, '.parquet');
    [X_val, y_val] = read_data(val_file);
    X_val = (X_val-meanX)./stdX;
    disp("Check fit on dev...")
    [predicted_labels, svm_output] = LS.predict(X_val);
    %% Save dev
    T = table(predicted_labels, svm_output, y_val);
    writetable(T, strcat(results_folder, "/dev_", num2str(i),".csv"))
    %% Other results
    [acc(i), tpr(i), tnr(i), f1(i)] = evaluate_results(predicted_labels, y_val);
    [~, ~, ~, auc_prec(i)] = perfcurve(y_val, svm_output, 1, 'XCrit', 'prec', 'YCrit', 'reca');
    [~, ~, ~, auc_roc(i)] = perfcurve(y_val, svm_output, 1);
    %% Load eval set
    SET = 'eval';
    val_file = strcat(FEATURES_DIR, SET, '.parquet');
    [X_val, y_val] = read_data(val_file);
    X_val = (X_val-meanX)./stdX;
    disp("Check fit on dev...")
    [predicted_labels, svm_output] = LS.predict(X_val);
    %% Save eval
    T = table(predicted_labels, svm_output, y_val);
    writetable(T, strcat(results_folder, "/eval_", num2str(i),".csv"))

end
