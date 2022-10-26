classdef TTmatrix
    %% Class Properties
    properties (Access = public)
        Size(:,4) {mustBeInteger,mustBeNonnegative,mustBeFinite}
        Cores(:,1) cell
        indexNorm(1,1) {mustBeInteger,mustBeNonnegative,mustBeFinite} = 0
        normError(1,1) = -1
    end
    %% Class Methods
    methods
        %% Class constructor
%   use default
        %% simple functions
        function r = rank(A)
            r = [1;A.Size(:,4)];
        end
        function d = ndims(A,varargin)
            if nargin == 1
                d = size(A.Size,1);
            elseif (nargin ==2) && isequal(varargin{1},'check')
                d = length(A.Cores);
            end
        end
        function [out,check] = size(A,varargin)
            if nargin == 1
                out = A.Size;
            elseif (nargin ==2) && isequal(varargin{1},'check')
                d = ndims(A,'check');
                out = zeros(d,4);
                for k=1:d
                    out(k,:) = size(A.Cores{k},[1 2 3 4]);
                end
                if ~isequal(A.Size,out)
                    warning("TTm.Size no longer the correct size of TTm, replace TTm.Size with output of this function.");
                    if nargout > 1
                        check = false;
                    end
                else
                    if nargout > 1
                        check = true;
                    end
                end
            elseif (nargin ==2) && isequal(varargin{1},1)
                out = A.Size(:,2);
            elseif (nargin ==2) && isequal(varargin{1},2)
                out = rank(A);
            else
                error("Invalid input");
            end
        end
        function [sizeMat] = matrixSize(TTm)
            sizeMat = [prod(TTm.Size(:,2)),prod(TTm.Size(:,3))];
        end
        
        %% methods defintion
        % operators
        C = plus(A,B);
        C = minus(A,B);
        C = times(A,B);
        C = mtimes(A,B);
        A = transpose(A);
        A = ctranspose(A);
        C = tkron(A,B);
        a = diag(A);
%         elems = subsref(A,s);

        % functions
        A = orthogonalize(A,n);
        normA = norm(A);
        A = rounding(A,par,opt);

    end
    methods (Static)
        A = eye(varargin);
    
    end
end