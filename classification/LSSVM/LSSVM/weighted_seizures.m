function [gamma] = weighted_seizures(y, gamma)
%WEIGHTED_SEIZURES(y, gamm) calculates the weights corresponding to the
%   positive and negative class of the output y.
%
%INPUT
%   y : output vector {-1,1}
%   gamma (scalar): regularization parameter
%
%OUTPUT
%   gamma (2 x 1): weighted regularization parameters. gamma(1): negative
%                   class, gamma(2): positive class. 


i_seiz = find(y == 1);
i_noseiz = find(y ==-1);

N_seiz = length(i_seiz);
N_noseiz = length(i_noseiz);

gamma_seiz = 0.5*gamma*(N_seiz + N_noseiz)/N_seiz;
gamma_noseiz = 0.5*gamma*(N_seiz + N_noseiz)/N_noseiz;


gamma = [gamma_noseiz; gamma_seiz];% gamma = zeros(N_noseiz+N_seiz,1);
% gamma(i_seiz) = gamma_seiz;
% gamma(i_noseiz) = gamma_noseiz;

end

