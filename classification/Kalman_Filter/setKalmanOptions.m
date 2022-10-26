function [options] = setKalmanOptions(varargin)
%setKalmanOptions() or setKalmanOptions(x0,p0,q,lambda,'r',rankX,rankP,rankC)
%   or setKalmanOptions(x0,p0,q,lambda,'e',epsX,epsP,epsC)
%   or setKalmanOptions(x0, p0, q, lambda, rankStruct, epsStruct)
%INPUT
%
%OUTPUT
%   options : struct with all the necessary Kalman filter options.


if nargin == 0
    prompt = 'Set x0. [zero/rand]:';
    options.x0 = input(prompt,'s');
    
    prompt = 'Set P0 = p0*eye(N), p0 = ';
    options.p0 = input(prompt);
    prompt = 'Quantization parameter for x: ';
    options.q = input(prompt);
    prompt = 'Forgetting factor lambda: ';
    options.lambda = input(prompt);
    prompt = "Truncate rank? [True/False]";
    options.Rank.trunc = input(prompt);
    if options.Rank.trunc
        prompt = 'Rank of x: ';
        options.Rank.x = input(prompt);
        prompt = 'Rank of P and W: ';
        options.Rank.P = input(prompt);
        prompt = 'Rank of C: ';
        options.Rank.C = input(prompt);
        options.Rank.maxX = 50;
        options.Rank.maxP = 5;
    end
    prompt = "Truncate error? [True/False]";
    options.Eps.trunc = input(prompt);
    if options.Eps.trunc
        prompt = 'Eps of x: ';
        options.Eps.x = input(prompt);
        prompt = 'Eps of P and W: ';
        options.Eps.P = input(prompt);
        prompt = 'Eps of C: ';
        options.Eps.C = input(prompt);
    end
elseif nargin == 7
    options.x0 = varargin{1};
    options.p0 = varargin{2};
    options.q = varargin{3};
    options.lambda = varargin{4};
    options.R = varargin{5};
    options.Rank = varargin{6};
    options.Eps = varargin{7};

elseif nargin > 7
    options.x0 = varargin{1};
    options.p0 = varargin{2};
    options.q = varargin{3};
    options.lambda = varargin{4};
    trunc = varargin{5};
    if trunc == 'r'
        options.Rank.trunc = true;
        options.Rank.x = varargin{6};
        options.Rank.P = varargin{7};
        options.Rank.C = varargin{8};
        options.Rank.maxX = 50;
        options.Rank.maxP = 5;
        options.Rank.maxC = 50;
        options.Eps.trunc = false;
    elseif trunc == 'e'
        options.Eps.trunc = true;
        options.Eps.x = varargin{6};
        options.Eps.P = varargin{7};
        options.Eps.C = varargin{8};
        options.Rank.trunc = false;
    end

end
