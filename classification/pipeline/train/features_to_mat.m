function features_to_mat(train_features, MAT_FILE, parameters)

disp("Loading Data...")

maxQ = 7;
% load training data
[X_train, y_train] = read_data(train_features);
disp("Loading parameters...")
[gamma, sigma2, opts] = load_parameters(parameters);

if ~contains(train_features, 'balanced')
    % if not balanced set use all seizure and sample non-seizure
    I_seiz = find(y_train == 1);
    I_noseiz = find(y_train == -1);
    N_seiz = length(I_seiz);
    N_tot = 2*N_seiz;
    [q, N_new] = getQTTpar(N_tot+1, maxQ);
    opts.kalmanOpt.q = q;
    N_new = N_new - 1;  % for bias
    if N_new/2 ~= N_seiz
        I_seiz = randsample(I_seiz, floor(N_new/2));
    end
    I_noseiz = randsample(I_noseiz, ceil(N_new/2));
    I_tot = [I_seiz(:); I_noseiz(:)];
    X_train = X_train(I_tot,:);
    y_train = y_train(I_tot);
else
    % with bias:
    X_train = X_train(1:end-1,:);
    y_train = y_train(1:end-1);
    
    %% check q
    N = length(y_train);
    opts.kalmanOpt.q = factor(N+1);
    if max(opts.kalmanOpt.q) > maxQ
        warning("Largest mode due to quantization is %d which is > %d.", max(opts.kalmanOpt.q), maxQ)
        [q, N_new] = getQTTpar(N+1, maxQ);
        disp(["New N = " + num2str(N_new)])
        opts.kalmanOpt.q = q;
        % idx = randsample(N, N_new - 1);
        X_train = X_train(1:N_new-1,:);
        y_train = y_train(1:N_new-1,:);
    end
end
%% Alternate data
disp("Alternating data...")
sizeX = size(X_train,1)
% First do a random permutation to shuffle up patients' data
I_perm = randperm(sizeX);
X_train = X_train(I_perm,:);
y_train = y_train(I_perm);
% alternate seizure and non-seizure datapoints
[X_train, y_train] = alternate_data(X_train, y_train);

size(X_train)
X_train = single(X_train);
y_train = single(y_train);

%% Normalize data
meanX = mean(X_train);
stdX = std(X_train);
X_train = (X_train - meanX)./stdX;

%% Saving data

disp("Saving training data...")
save(MAT_FILE, 'X_train', 'y_train', 'sigma2', 'gamma', 'opts', 'meanX','stdX', '-v7.3')
end