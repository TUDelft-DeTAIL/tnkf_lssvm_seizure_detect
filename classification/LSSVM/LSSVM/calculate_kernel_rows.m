% clearvars
% setup
% %% Which PC
% LAPTOP = true;
% CLUSTER = false;
% SERVER = false;
% 
% if LAPTOP
%     FEATURE_DIR = "C:\Users\selinederooij\Documents\tuh_eeg_seizure\Features\";
% elseif CLUSTER
%     FEATURE_DIR = "/scratch/selinederooij/Features/";
% elseif SERVER
%     FEATURE_DIR = "/space/selinederooij/Features/";
% end
% 
% %% DIRS
% TRAINING_FILE = FEATURE_DIR+"train/data.mat";
% KERNEL_FILE = FEATURE_DIR+"train/kernel_rows.mat";
% train_features = FEATURE_DIR+"balanced_train.parquet";
% parameters = "parameters.json";

function calculate_kernel_rows(TRAINING_FILE, KERNEL_FILE, parameters, train_features, k_start, k_end)
%calculate_kernel_rows(TRAINING_FILE, KERNEL_FILE, parameters, train_features)

%% Load data to memory
% test:
disp("Loading Data...")

try 
    load(TRAINING_FILE)
    whos
    N = length(y_train);
catch
    maxQ = 10;
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
        disp(["New N = " + num2str(N_new)])
        opts.kalmanOpt.q = q;
        % idx = randsample(N, N_new - 1);
        X_train = X_train(1:N_new-1,:);
        y_train = y_train(1:N_new-1,:);
        N = N_new;
    end

    %% Alternate data
    disp("Alternating data...")
    size(X_train)
    [X_train, y_train] = alternate_data(X_train, y_train);
    size(X_train)
    whos

    %% Normalize
    meanX = mean(X_train, 1);
    stdX = std(X_train, 1);
    X_train = (X_train - meanX)./(stdX);
    %% Saving data
    disp("Saving training data...")
    save(TRAINING_FILE, 'X_train', 'y_train', 'sigma2', 'gamma', 'opts', ...
        'meanX', "stdX", '-v7.3')
end

%% Calculate kernel rows
disp("Calculate kernel rows...")
batchSize = 200;
rankC = opts.kalmanOpt.Rank.C;
epsC = opts.kalmanOpt.Eps.C;
q = opts.kalmanOpt.q;
total_iter = ceil(N/batchSize);
% C = cell(total_iter,1);
C = cell(batchSize,total_iter);
y_train = single(y_train);
X_train = single(X_train);
whos

tic
for k = 0:total_iter-1
    begin_row = k*batchSize + 1;
    end_row = min(k*batchSize + batchSize, N);
    idx_row = begin_row:end_row;

    rows = kernel_row(X_train, y_train, gamma, sigma2, idx_row);

    temp = cell(batchSize,1);
%     C{k+1} = Mat2TTm([y_train(idx_row), rows], factor(batchSize),q,rankC,'r');
    for i = 1:size(rows,1)
        temp{i} = Vec2TT([y_train(idx_row(i)), rows(i,:)], ...
                q, rankC, epsC);
%         if i > 1
%             temp{i} = TT_ALS(Vec2Tens([y_train(idx_row(i)), rows(i,:)],q), temp{i-1}, 1e-3,1);
%         else
%             temp{i} = Vec2TT([y_train(idx_row(i)), rows(i,:)], ...
%                 q, rankC, epsC);
%         end
    end
    C(:,k+1) = temp;
    % toc
    % exit
end
toc

%% Clear X and reshape C
clear X_train y_train

C = reshape(C, [], 1);

%% Save kernel_rows
disp("Saving kernel rows...")
save(KERNEL_FILE, 'C', '-v7.3')

%% Exiting
disp("exit(0)")

end