function [neg_weight, pos_weight] = weights(y, gamma)
%WEIGHTED_SEIZURES(y, gamm) calculates the weights corresponding to the
%   positive and negative class of the output y.
%
%INPUT
%   y : output vector {-1,1}
%   gamma (scalar): regularization parameter
%
%OUTPUT
%   neg_weight
%   pos_weight


i_seiz = find(y == 1);
i_noseiz = find(y ==-1);

N_seiz = length(i_seiz);
N_noseiz = length(i_noseiz);

pos_weight = 0.5*gamma*(N_seiz + N_noseiz)/N_seiz;
neg_weight = 0.5*gamma*(N_seiz + N_noseiz)/N_noseiz;



end

