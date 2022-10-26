function update_param(TRAINING_FILE,parameters)

T = matfile(TRAINING_FILE, 'Writable', true)
disp("Loading parameters...")
[gamma, sigma2, ~] = load_parameters(parameters);
T.gamma = gamma
T.sigma2 = sigma2



end