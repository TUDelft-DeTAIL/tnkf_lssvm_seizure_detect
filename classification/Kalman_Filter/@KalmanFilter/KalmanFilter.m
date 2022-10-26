classdef KalmanFilter
    %% Class Properties
    properties (Access = public)
        x
        P
        R
        Options 
    end

    %% Class Methods
    methods
        %% Constructor
        function obj = KalmanFilter(x,P,R,Options)
            %KalmanFilter(x,P,R,Options)
            obj.x = x;
            obj.P = P;
            obj.R = R;
            obj.Options = Options;
            
        end

        
        %% Functions
        obj = Update(obj,y,C);
    end
end
