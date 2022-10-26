classdef TensorTrain
    %% Class Properties
    properties (Access = public)
        Size(:,3) {mustBeInteger,mustBeNonnegative,mustBeFinite}
        Cores(:,1) cell
        indexNorm(1,1) {mustBeInteger,mustBeNonnegative,mustBeFinite} = 0
        normError(1,1) = -1
    end
    %% Class Methods
    methods
        %% Constructor
%         function obj = TensorTrain(varargin)
%             if nargin == 1
%                 tens = varargin{1};
%                 switch class(tens)
%                     case 'cell'
%                         obj.Cores = tens;
%                         N = length(tens);
%                         obj.Size = zeros(N,3);
%                         for k = 1:N
%                             obj.Size(k,:) = size(tens{k},[1 2 3]);
%                         end
%                     case 'struct'
%                         obj.Cores = tens.Cores;
%                         obj.Size = tens.Size;
%                     otherwise
%                         error('Specified input incorrect')
%                 end
%             elseif nargin == 2
%                 obj.Size = varargin{2};
%                 obj.Cores = varargin{1};
%             end
%         end
        
        %% simple functions
        function r = rank(A)
            r = [1;A.Size(:,3)];
        end
        function d = ndims(A,varargin)
            if nargin == 1
                d = size(A.Size,1);
            elseif (nargin ==2) && isequal(varargin{1},'check')
                d = length(A.Cores);
            end
        end
        function [sz,check] = size(A,varargin)
            if nargin == 1
                sz = A.Size;
            elseif (nargin ==2) && isequal(varargin{1},'check')
                d = ndims(A,'check');
                sz = zeros(d,3);
                for k=1:d
                    sz(k,:) = size(A.Cores{k},[1 2 3]);
                end
                if ~isequal(A.Size,sz)
                    warning("TT.Size no longer the correct size of TT, replace TT.Size with output of this function.");
                    if nargout > 1
                        check = false;
                    end
                else
                    if nargout > 1
                        check = true;
                    end
                end
            elseif (nargin ==2) && isequal(varargin{1},1)
                sz = A.Size(:,2);
            elseif (nargin ==2) && isequal(varargin{1},2)
                sz = rank(A);
            else
                error("Invalid input");
            end
        end
        function l = length(A)
            l = ndims(A);
        end

        

        %% methods defintion
        % operators
        C = plus(A,B);
        C = minus(A,B);
        C = times(A,B);
        C = mtimes(A,B);
%         elems = subsref(A,s);
        
        % functions
        A = orthogonalize(A,n);
        normA = norm(A);
        A = rounding(A,par,opt);
        cores = leftcores(A, n);
        cores = rightcores(A,n);
        A = shiftnorm(A,n);

    end
    methods (Static)
        A = zeros(varargin);
        A = ones(varargin);

    end
end