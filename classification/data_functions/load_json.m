function s = load_json(filename)
%LOAD_JSON loads a json file into a matlab struct.
%
%INPUT
%   filename : name of json file
%OUTPUT
%   s : (struct) containing content of json file


fid = fopen(filename);
raw = fread(fid, inf);
str = char(raw');
fclose(fid);
s = jsondecode(str);



end