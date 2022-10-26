function [X, y] = read_data(datafile, varargin)
%READ_DATA load the features and labels from the data file into memory and
%   assign to parameters X and y

% Get extension of file
[~,~,ext] = fileparts(datafile);

switch ext
    case ".parquet"
        p = parquetinfo(datafile);
        featureNames = p.VariableNames(contains(p.VariableNames,"|"));
        requestNames = ["annotation", featureNames];
        T = parquetread(datafile, "SelectedVariableNames", requestNames);
        y = T.annotation;
        T.annotation = [];

        % since matlab downcast to int but we need floats
%         X = T{:,:};
        X = single(zeros(size(T)));
        for k = 1:size(T,2)
            X(:,k) = single(T{:,k});
        end
        
    case ".csv"

        T = readtable(datafile, "ReadVariableNames", true);
        columns = T.Properties.VariableNames;
        features = contains(columns, "|");
        X = T(:,features);
        y = T.annotation;

    case ".mat"
        T = load(datafile);
        X = T.X;
        y = double(T.y);
    otherwise
        error("Invalid input format specified")
     
end

