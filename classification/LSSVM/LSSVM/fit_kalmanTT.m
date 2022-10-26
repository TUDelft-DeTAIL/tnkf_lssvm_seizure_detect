function LS = fit_kalmanTT(LS)
%fit_kalmanTT(LS) fits/trains the LSSVM object using the TNKF method.
%   The LSSVM object needs to be initialized first with the training set.
%
%INPUT
%   LS : untrained LSSVM object
%
%OUTPUT
%   LS : trained LSSVM object

N = length(LS.y_train);
opts = LS.Options.kalmanOpt;
if LS.k == 0
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
    C = Vec2TT([0; LS.y_train(:)], opts.q, opts.Rank.C, opts.Eps.C);
    filt = filt.Update(0, C); % y[0] = 0
    LS.k = 1;
else
    filt = KalmanFilter(LS.x_bar, LS.P_bar, opts.R, opts);
end
    
%     % k > 0
%     for k = 1:N
%         C = Vec2TT([LS.y_train(k), kernel_row(LS,k)], opts.q, opts.Rank.C, opts.Eps.C);
%         filt = filt.Update(1, C); %y[k] = 1
%         LS.k = k;
%     end
% elseif LS.k > 0 && LS.k < N

for k = LS.k:N
    C = Vec2TT([LS.y_train(k), kernel_row(LS,k)], opts.q, opts.Rank.C, opts.Eps.C);
    filt = filt.Update(1, C); %y[k] = 1
    LS.k = k;
end


LS.x_bar = filt.x;
LS.P_bar = filt.P;
% x = TT2Vec(filt.x);

% LS.b = x(1);
% LS.alpha = x(2:end);

end