function [Accuracy, TPR, TNR,F1] = evaluate_results(y_t, labels)
%[Accuracy, TPR, TNR,F1] = evaluate_results(y_t, labels)
%EVALUATE_RESULTS Summary of this function goes here
%   Detailed explanation goes here

y_t = single(y_t);
labels = single(labels);

diff_labels = (y_t - labels);
true_labels = find(diff_labels  == 0);
TP = sum(labels(true_labels) == 1);
TN = sum(labels(true_labels) == -1);
FP = length(find(diff_labels == -2));
FN = length(find(diff_labels == 2));
Positives = TP+FN;
Negatives = FP+TN;
Accuracy = (TP+TN)/(Positives+Negatives);
TNR = TN/Negatives;
TPR = TP/Positives;

F1 = TP/(TP + 0.5*(FP+FN));


end

