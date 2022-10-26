function LS = train_model(train_features, kernel_folder, outputfile)

%% Load data to memory
% test:
disp("Loading Data...")
datafile = matfile(train_features);
gamma = datafile.gamma;
sigma2 = datafile.sigma2;
opts = datafile.opts;
% y_train = datafile.y_train;
opts.kalmanOpt.Rank.x = 30;
disp(opts.kalmanOpt.Rank)

%% Load kernel rows
disp("Loading kernel row files...")
C_files = dir(strcat(kernel_folder, "kernel_rows*.mat"));
C_files = cellstr(strcat(kernel_folder,string(natsortfiles({C_files.name}'))));    % using https://www.mathworks.com/matlabcentral/fileexchange/47434-natural-order-filename-sort?s_tid=ta_fx_results

%% Start Training
% Initialize LSSVM object
LS = LSSVM([], [], "RBF_kernel", sigma2, gamma, opts, []);
LS.savefile = outputfile;
%% Train (and time)
disp("Training data...")
tic;
LS = LS.fit(C_files);
toc;
%% SAVE
disp("Saving trained model...")
LS.C_files = [];
LS.X_train = datafile.X_train;
LS.y_train = datafile.y_train;
save(outputfile, "LS", '-v7.3')

end


