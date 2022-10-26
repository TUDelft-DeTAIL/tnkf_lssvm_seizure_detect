classdef LSSVM
    %LSSVM(X_train, y_train, kernel_type, kernel_pars, gamma, Options)
    %% Class Properties
    properties (Access = public)
        alpha
        b
        kernel_type
        kernel_pars
        gamma
        X_train
        y_train
        x_bar
        P_bar
        C_files
        status
        k
        Options
        results
        savefile
    end
    properties (Access = private)
        orig_gamma
        neg_weight
        pos_weight
    end

    %% Class Methods
    methods
        %% Constructor
        function obj = LSSVM(X_train, y_train, kernel_type, kernel_pars, gamma, Options, C)
            %LSSVM(X_train, y_train, kernel_type, kernel_pars, gamma, Options)
            
            if length(y_train) ~= size(X_train,1)
                error("Features length and output length do not match.")
            end
            obj.Options = Options;
            obj.orig_gamma = gamma;
            obj.X_train = X_train;
            obj.y_train = y_train;
            obj.x_bar = [];
            obj.P_bar = [];
            obj.kernel_type = kernel_type;
            obj.kernel_pars = kernel_pars;
%             obj.gamma = gamma;
            obj.status = 'init';
            obj.k = 0;
            obj.alpha = [];
            obj.b = [];
            obj.savefile = [];
            obj.Options.weighted = false;
            obj.gamma = obj.orig_gamma;
            if nargin > 6
                obj.C_files = C;
            else
                obj.C_files = [];
            end



            % uncomment below for weighted options
%             if length(gamma) == length(y_train)
%                 obj.Options.weighted = true;
%             elseif Options.weighted % calculate weights based on seiz/nonseiz distribtion.
% %                     obj.gamma = weighted_seizures(y_train, gamma);
%                 [obj.neg_weight, obj.pos_weight] = weights(y_train, gamma);
%                 obj.gamma = [obj.orig_gamma*obj.neg_weight; obj.orig_gamma*...
%                     obj.pos_weight];
%             else
%                 obj.Options.weighted = false;
%                 obj.gamma = obj.orig_gamma;
%                 
%             end
            obj.results = [];
        end


        %% set methods
%         function obj = set.y_train(obj, val)
%             obj.y_train = val;
%             if obj.Options.weighted
%                 obj.gamma = obj.orig_gamma;
%             end
%         end
% 
%         function obj = set.gamma(obj, val)
%             if obj.Options.weighted
%                 if length(val) == 1
%                     obj.orig_gamma = val;
%                     [obj.neg_weight, obj.pos_weight] = weights(obj.y_train, val);
%                     obj.gamma = [obj.orig_gamma*obj.neg_weight; obj.orig_gamma*...
%                         obj.pos_weight];
%                 else
%                     obj.gamma = val;
%                 end
%             else
%                 obj.gamma = val;
%             end
%             
%         end



        %% get methods
%         function val = get.gamma(obj)
%             if obj.Options.weighted
%                 val = [obj.gamma*obj.neg_weight; obj.gamma*obj.pos_weight];
%             else
%                 val = obj.gamma;
%             end
%         end

      
        %% Functions
        obj = fit(obj, C_files);
        [labels,z, y_var] = predict(obj, X_test);
        kernelRow = kernel_row(obj, k, varargin);
        obj = crossval(obj,cv);
        obj = hyperopt(obj, method, k, gamma, kernel_par, TT_ranks)
    end
end

