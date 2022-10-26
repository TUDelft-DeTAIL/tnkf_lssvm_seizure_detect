function [q, Nnew] = getQTTpar(N, varargin)
%GETQTTPAR get new quantization parameters for.
%   Detailed explanation goes here
%
%INPUT
%   N
%   maxRank
%
%OUTPUT
%   q : quantization vector
%   N_new : new length of data

maxRank = 20;    % default maxRank
if nargin > 1
    maxRank = varargin{1};
end

q = factor(N);
Nnew = N;
if max(q) <= maxRank
    return
end

while max(q) > maxRank
    Nnew = Nnew - 1;
    q = factor(Nnew);
end

end

