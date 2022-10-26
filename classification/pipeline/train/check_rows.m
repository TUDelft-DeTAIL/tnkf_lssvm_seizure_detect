function check_rows(kernel_folder)


disp("Loading kernel row files...")
C_files = dir(strcat(kernel_folder, "kernel_rows_*.mat"));
C_files = cellstr(strcat(kernel_folder,string(natsortfiles({C_files.name}'))));    % using https://www.mathworks.com/matlabcentral/fileexchange/47434-natural-order-filename-sort?s_tid=ta_fx_results


for i = 1:length(C_files)
    disp(i)
    T = load(C_files{i});
    clear T
end

disp("All good")

end