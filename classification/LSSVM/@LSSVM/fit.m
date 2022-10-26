function obj = fit(obj, C_files)
%FIT Summary of this function goes here
%   Detailed explanation goes here


switch obj.Options.method
    case "regular"
        [obj.alpha, obj.b] = lssvm_classify(obj.X_train, obj.y_train, ...
            obj.kernel_type, obj.kernel_pars, obj.gamma);
        obj.status = 'trained';

    case "kalman"
%         [obj.alpha, obj.b] = lssvm_classify_kalman(obj.X_train, obj.y_train, ...
%             obj.kernel_type, obj.kernel_pars, obj.gamma);
        obj = fit_kalman_row(obj);
        obj.status = 'trained';

    case "kalmanTT"
        if nargin == 1
            obj = fit_kalmanTT(obj);
        else
            obj = fit_TT_with_kernel(obj, C_files);
        end
        obj.status = 'trained';
        
    otherwise
        error("LSSVM method "+ obj.Options.method + " not valid.")
end

end








