% function train_tusz(train_features, parameters, validation_file, output_file)
%TRAIN_TUSZ Summary of this function goes here
%   Detailed explanation goes here


setup
%% Load data to memory
% test:
disp("Loading Data...")
% PROJECT_DRIVE = "~/ProjectDrive/staff-umbrella/"
if isunix
    train_features = "/space/selinederooij/TUSZ/train/balanced_train.parquet";
       % Code to run on Linux platform
elseif ispc
    train_features = "U:\Seizure Data\v1.5.2\Features\balanced_train.parquet";   % Code to run on Windows platform
else
    disp('Platform not supported')
end

parameters = "parameters.json";
maxQ = 20;
% load training data
[X_train, y_train] = read_data(train_features);

%% load parameters
disp("Loading parameters...")
[gamma, sigma2, opts] = load_parameters(parameters);
N = length(y_train);
opts.kalmanOpt.q = factor(N+1);
if max(opts.kalmanOpt.q) > maxQ
    warning("Largest mode due to quantization is %d which is > %d.", max(opts.kalmanOpt.q), maxQ)
    [q, N_new] = getQTTpar(N+1, maxQ);
    disp(["New N = ",num2str(N_new)])
    opts.kalmanOpt.q = q;
    % idx = randsample(N, N_new - 1);
    X_train = X_train(1:N_new-1,:);
    y_train = y_train(1:N_new-1,:);
end

%% Alternate data
disp("Alternating data...")
size(X_train)
[X_train, y_train] = alternate_data(X_train, y_train);
size(X_train)

%% Start Training
% Initialize LSSVM object
LS = LSSVM(X_train, y_train, "RBF_kernel", sigma2, gamma, opts);

% clear X_train y_train % remove from memory
% Train (and time)
disp("Training data...")
tic;
LS = LS.fit();
toc;

save("trained_LS.mat", "LS", "-mat")

% %% Validate 
% % load validation data
% [X_val, y_val] = read_data(validation_file);
% 
% [labels, svm_output] = LS.predict(X_val);
% results = get_results(labels, svm_output, y_val);
% 
% print_results_summary(results);
% 
% %% save to output file
% 
% save(output_file, "LS", "results", "-mat");


% end

