function kernel_rows_slurm(TRAINING_FILE, KERNEL_FILE, Ntasks, iter)
%kernel_rows_slurm(TRAINING_FILE, KERNEL_FILE, Ntasks, iter)
%   for computing on SLURM cluster

%% Load data to memory
% test:
disp("Loading Data...")

disp(TRAINING_FILE)
T = load(TRAINING_FILE)
whos
N = length(T.y_train)

if ~exist('T.sigma2','var')
    [T.gamma, T.sigma2, T.opts] = load_parameters('parameters.json');
end

%% Calculate kernel rows
disp("Calculate paremeters...")
T.opts.kalmanOpt
rankC = T.opts.kalmanOpt.Rank.C;
epsC = T.opts.kalmanOpt.Eps.C;
q = T.opts.kalmanOpt.q;
if isempty(q)
    q = factor(N+1)
end
%% Calculate which iterations to perform
disp(strcat("Ntasks = ", num2str(Ntasks)))
disp(strcat("iter = ", num2str(iter)))
Ntot = N + 1;      % including first row
total_rows = floor(N/Ntasks)
k_start = iter*total_rows + 1
k_end = iter*total_rows + total_rows

if iter == (Ntasks-1) && rem(N,Ntasks) ~= 0  % start at 0
    total_rows = total_rows + rem(N,Ntasks)
    k_end = N; %k_end + rem(Ntot,Ntasks)
% elseif iter == 0
%      total_rows = total_rows -1
end

C = cell(total_rows,1);
y_train = single(T.y_train);
X_train = single(T.X_train);
clear T.y_train T.X_train
% whos
%% Start iterations
disp("Starting iterations...")
q
batchSize = 200;
if k_start == 1
    C_1 = Vec2TT([0; y_train(:)], q, rankC, epsC);
end

tic

k_C = 1:batchSize:total_rows;   % indices for C
k_C(end+1) = total_rows+1;

counter = 1;
for k = k_start:batchSize:k_end
    if rem(counter, 100) == 0
        disp(strcat("counter = ",num2str(counter)))
    end

    begin_row = k;
    end_row = min([k+batchSize-1, k_end]);
    idx_row = begin_row:end_row;
    rows = kernel_row(X_train, y_train, T.gamma, T.sigma2, idx_row);
    temp = cell(size(rows,1),1);
    
    for i = 1:size(rows,1)
        temp{i} = Vec2TT([y_train(idx_row(i)), rows(i,:)], ...
                q, rankC, epsC);
    end      

    C(k_C(counter):k_C(counter+1)-1) = temp;
    counter = counter + 1;  % counter
end
toc

%% Clear X and reshape C
clear X_train y_train
if exist('C_1', 'var')
    C = [{C_1}; C];
end

%% Save kernel_rows
disp("Saving kernel rows...")
KERNEL_FILE = erase(KERNEL_FILE,'.mat');
save(strcat(KERNEL_FILE,"_",num2str(iter),".mat"), 'C', '-v7.3')

%% Exiting
disp("exit(0)")

end