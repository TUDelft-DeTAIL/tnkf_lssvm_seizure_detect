function [Rank] = setRank(d,min_rank,max_rank,varargin)
%setRank(d,min_rank,max_rank,'l') OR setRank(d,min_rank,max_rank,'p') 
%   calculates an expression for the maximum TT-ranks by interpolating
%   between min_rank and max_rank. This interpollation can be done linearly
%   (option 'l') or parabolically (options 'p'). The default is linear.
%
%INPUT
%   d : dimension of TT (decides length of rank-vector)
%   min_rank : minimum maximal rank
%   max_rank : maximum maximal rank
%   (opt.) 'l' or 'p' : linear or parabolic interpolation.
%OUTPUT
%   Rank : vector with maximum ranks.

if nargin ==3
    Rank = setRankLinear(d,min_rank,max_rank);
else 
    switch varargin{1}
        case 'l'
            Rank = setRankLinear(d,min_rank,max_rank);
        case 'p'
            Rank = setRankParabolic(d,min_rank,max_rank);
    end
end

end

function [Rank] = setRankLinear(d,min_rank,max_rank)
Rank = zeros(1,d+1);
Rank(1) = 1;
d_1 = ceil(d/2);
alpha_1 = (max_rank-min_rank)/(d_1-1);
for k = 2:d_1+1
    Rank(k) = ceil(alpha_1*(k-2)+min_rank);    
end
d_2 = d-1-d_1;
%alpha_2 = (max_rank-min_rank)/(d_2);
for k = 0:d_2
    Rank(d-k) = ceil(alpha_1*k+min_rank);
    
end

Rank(d+1) = 1;
end

function [Rank] = setRankParabolic(d,min_rank,max_rank)


d_half = floor(d/2);
coef = (min_rank-max_rank)/(d_half^2);
Rank = zeros(1,d_half);
Rank(1) = 1;
for k = 2:d_half
    Rank(k) = round(coef*(-d_half+k-2)^2+max_rank);
end

if mod(d,2) == 0
  % d is even
  Rank = [Rank,max_rank, flip(Rank)];
else
  % d is odd
  Rank = [Rank, max_rank,max_rank,flip(Rank)];
end


end

