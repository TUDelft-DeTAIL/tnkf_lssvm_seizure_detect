function C = plus(A,B)
%plus(A,B) performs the addition of two TTmatrix A and B.
%
%INPUT
%   A : TTmatrix
%   B : TTmatrix
%OUTPUT
%   C : C = A+B, TTmatrix

C = TTmatrix;

szA = A.Size;
szB = B.Size;
rA = rank(A);%szA(1:end-1,3); %ranks r_2--r_{d-1}
rB = rank(B);%szB(1:end-1,3);
nA = szA(1:end,2);
nB = szB(1:end,2);
mA = szA(1:end,3);
mB = szB(1:end,3);
coresA = A.Cores;
coresB = B.Cores;

d = ndims(A);
if ~isequal(nA,nB)||~isequal(mA,mB)
    error("Size of TT's inconsistent");
end

rC = rA(2:d)+rB(2:d);
n = nA;
m = mA;
C.Size = [[1;rC],n,m,[rC;1]];
coresC = cell(d,1);
C.Cores = cell(d,1);

%% Concatenate cores
% first core
coresC{1} = zeros(C.Size(1,:));
coresC{1}(1,:,:,1:rA(2)) = coresA{1};
coresC{1}(1,:,:,rA(2)+1:rA(2)+rB(2)) = coresB{1};

for k = 2:d-1
   coresC{k} = zeros(C.Size(k,:));
   coresC{k}(1:rA(k),:,:,1:rA(k+1)) = coresA{k};
   coresC{k}(rA(k)+1:rA(k)+rB(k),:,:,rA(k+1)+1:rA(k+1)+rB(k+1)) = coresB{k};
end

coresC{d} = zeros(C.Size(d,:));
coresC{d}(1:rA(d),:,:,1) = coresA{d};
coresC{d}(rA(d)+1:rA(d)+rB(d),:,:,1) = coresB{d};


C.Cores = coresC;
C.indexNorm = 0;

