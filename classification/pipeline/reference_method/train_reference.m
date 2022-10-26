% To train a regular LSSVM

config; % load global parameters
N = 1e4; % for lssvm

[X, y] = read_data(TRAIN_FEATURES);
X = single(X);
y = single(y);

N_tot = length(y);
n_sims = 1;
I_seiz = find(y == 1);
I_noseiz = find(y == -1);

if ~isfolder(strcat(FEATURES_DIR,'train/lssvm/'))
    mkdir(strcat(FEATURES_DIR,'train/lssvm/'))
end

for k = 1:n_sims
    %% Sample
    I_seiz_k = randsample(I_seiz, floor(N/2));
    I_noseiz_k = randsample(I_noseiz, ceil(N/2));
    
    %% Extract the seiz/non-seiz samples
    I_tot = [I_seiz_k(:);I_noseiz_k(:)];
    
    X_train = X(I_tot,:);
    y_train = y(I_tot);

    save(strcat(FEATURES_DIR,'train/lssvm/data_',num2str(k),'.mat'), ...
        'X_train', 'y_train')
    %% initialize model 
%     meanX = mean(X);
%     stdX = std(X);
%     X = (X-meanX)./stdX;
    model = initlssvm(X_train, y_train, 'classifier', 0.1, 1, 'RBF_kernel', ...
        'preprocess');
    %% Tune hyperparameters
    
    model = tunelssvm(model, 'gridsearch', 'crossvalidatelssvm', ...
        {5, 'misclass'});
    
    %% Train full model
    model = trainlssvm(model); 
    
    %% Save trained model
%     save(strcat(FEATURES_DIR,'train/reference_model_normalized.mat'), 'model', 'meanX','stdX', '-v7')
    save(strcat(FEATURES_DIR,'train/lssvm/model_',num2str(k),'.mat'), ...
        'model', '-v7')
end