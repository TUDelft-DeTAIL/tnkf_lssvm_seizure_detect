function obj = Update(obj, y_kalman, C)
%Update(obj,y,C) performs the Kalman filter update step.


if isa(obj.x,'TensorTrain')
    [obj.x,obj.P] = ...
        kalmanUpdateTTRow(obj.x,y_kalman,C,obj.P,obj.R, obj.Options); % simplify to
elseif isa(obj.x,'double')
    W = 0;
    [obj.x, obj.P] = ...
        kalmanUpdateMat(obj.x,y_kalman,C,obj.P,W,obj.R); % simplify to
else
    error("incorrect datatype")

end

