function LS = fit_TT_with_kernel(LS, C_files)
%FIT_TT_WITH_KERNEL Kernel rows already precalculated
%   Detailed explanation goes here
%INPUT
%   LS : untrained LSSVM object
%   C_files : cell with names/paths of mat files containing kernel rows
%
%OUTPUT
%   LS : trained LSSVM object
t0 = tic;
numC_files = length(C_files);
load(C_files{1}, 'C');
C = C(~cellfun(@isempty,C)); % remove empty rows

opts = LS.Options.kalmanOpt;

%% Initialize x and P
if strcmp(opts.x0,'zero')
    x = zeros(opts.q, 'TensorTrain');
elseif isa(opts.x0, 'TensorTrain')
    x = opts.x0;
else
    x = zeros(opts.q, 'TensorTrain');   % default to zero initialization
end

P = eye(opts.q, 'TTmatrix') * opts.p0;

%% Kalman Filter
% Create filter object
filt = KalmanFilter(x, P, opts.R, opts);

%% First iteration
% k = 0
disp("start iter with file 0")
filt = filt.Update(0, C{1}); % y[0] = 0
LS.k = 0;
%% next iterations
t1 = tic;
for k = 2:length(C)
    filt = filt.Update(1,C{k});
end
toc(t1)

LS.x_bar = filt.x;
LS.P_bar = filt.P;
LS.k = 1;
save(LS.savefile,'LS')
clear C

for i = 2:numC_files
    disp(["start iter with file ", num2str(i-1)])
    load(C_files{i}, 'C')
    C = C(~cellfun(@isempty,C)); % remove empty rows
    t1 = tic;
    for k = 1:length(C)
        filt = filt.Update(1, C{k}); %y[k] = 1
    end
    toc(t1)
    LS.x_bar = filt.x;
    LS.P_bar = filt.P;
    LS.k = i;
    save(LS.savefile,'LS')
    clear C
end
toc(t0)

LS.x_bar = filt.x;
LS.P_bar = filt.P;

x = TT2Vec(filt.x);
 
LS.b = x(1);
LS.alpha = x(2:end);

end

