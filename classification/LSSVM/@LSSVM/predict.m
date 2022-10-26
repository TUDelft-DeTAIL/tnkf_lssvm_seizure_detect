function [labels, classifier_output, variance_output] = predict(obj, X_test)
%[labels, classifier_output, variance_output] = predict(obj, X_test)

switch obj.Options.method
    case "regular" 
        [labels, classifier_output] = lssvm_predict(obj.alpha, obj.b, obj.X_train, X_test, ...
            obj.y_train, obj.kernel_type, obj.kernel_pars);
    case "kalman"
        [labels, classifier_output] = lssvm_predict(obj.alpha, obj.b, obj.X_train, X_test, ...
            obj.y_train, obj.kernel_type, obj.kernel_pars);
    case "kalmanTT"

        if isempty(obj.alpha)
            x = TT2Vec(obj.x_bar);
            obj.alpha = x(2:end);
            obj.b = x(1);
        end
        [labels, classifier_output] = lssvm_predict(obj.alpha, obj.b, obj.X_train, X_test, ...
            obj.y_train, obj.kernel_type, obj.kernel_pars);


    otherwise
        error("LSSVM method"+ obj.Options.method + "not valid.")
end

end




% Prediction function for TT's
function [labels, classifier_output, variance_output] = predict_kalmanTT(obj, X_test)
%[labels, classifier_output, variance_output] = predict_kalmanTT(obj, X_test)
%TODO: add batches for kernel_row calculation

opts = obj.Options.kalmanOpt;
q = opts.q;
rankC = opts.Rank.C;
epsC = opts.Eps.C;
y_train = Vec2TT([1; obj.y_train(:)], q, 20, 0.001);        % add 1 for the bias
XtY = obj.x_bar.*y_train;


N_test = size(X_test,1);
batchSize = 200;
iters = 1:batchSize:N_test;
total_iter = length(iters);
% initialize
classifier_output =cell(total_iter,1);% zeros(total_iter,batchSize);
variance_output = cell(total_iter,1); %zeros(size(classifier_output));

% X_test_cell = cell(total_iter,1);
% for ii = 1:total_iter
%     X_test_cell{ii} = X_test(1:min(batchSize, size(X_test,1)),:);
%     X_test(1:min(batchSize, size(X_test,1)),:) = [];
% end

X_train = obj.X_train;
obj.X_train = [];
kernel_type = obj.kernel_type;
kernel_pars = obj.kernel_pars;
P_bar = obj.P_bar;
R = opts.R;
clear obj;

parfor k = 1:total_iter
    disp(strcat("Batch ",num2str(k)))
    begin_row = iters(k);
    end_row = min([iters(k)+batchSize-1, N_test]); 
    idx_row = begin_row:end_row;
    n_rows = length(idx_row);
    rows = kernel_matrix(X_train, kernel_type, kernel_pars, X_test(idx_row,:));

    temp_output = zeros(n_rows,1);
    temp_variance = temp_output;
    for i = 1:n_rows
        C = Vec2TT([1; rows(:,i)], q, rankC, epsC);
        % C = Vec2TT([1; kernel_matrix( ...
        %     obj.X_train, obj.kernel_type, obj.kernel_pars, X_test(k,:))], ...
        %     q, rankC, epsC);    % add 1 for the bias
        % prediction function
        temp_output(i) = dot(C, XtY);
        % uncertainty bound
        temp_variance(i) = dot(C,P_bar*C) + R;
    end

    classifier_output{k} = temp_output(:);
    variance_output{k} = temp_variance(:);

end
% reshape and select indices
classifier_output = cell2mat(classifier_output);
variance_output = cell2mat(variance_output);

labels = sign(classifier_output);

end