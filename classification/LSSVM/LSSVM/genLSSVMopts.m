function opt = genLSSVMopts(method, type, kalmanOpt)

opt = struct('method', method, 'type', type);
if strcmp(method,'kalmanTT')
    opt.kalmanOpt = kalmanOpt;
end

end