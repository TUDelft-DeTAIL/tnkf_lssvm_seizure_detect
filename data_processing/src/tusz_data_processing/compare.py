import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import seaborn as sns
from sklearn import metrics
import matplotlib

# matplotlib.rcParams['mathtext.fontset'] = 'stix'
# matplotlib.rcParams['font.family'] = 'calibri' #'STIXGeneral'
matplotlib.rcParams["font.size"] = 15
plt.rc("legend", fontsize=14)
"""
    Global Variables  
"""
# PATIENT = 4473
# SVM_PATH = "../classification/results/4473/"
TNKF_PATH = "C:/Users/selinederooij/surfdrive/Data/TUG_EEG_Corpus/TNKF_LSSVM_Seizure_Detect/results/patient_independent/"


def plot_additional_lines(ax, tprs, mean_fpr, aucs):

    ax.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        lw=2,
        color="lightcoral",
        label="Chance",
        alpha=0.8,
    )

    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = metrics.auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    ax.plot(
        mean_fpr,
        mean_tpr,
        color="mediumblue",
        label=r"Mean (AUC = %0.2f $\pm$ %0.2f)" % (mean_auc, std_auc),
        lw=4,
    )

    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    ax.fill_between(
        mean_fpr,
        tprs_lower,
        tprs_upper,
        color="grey",
        alpha=0.2,
        label=r"$\pm$ 1 std. dev.",
    )

    ax.set(
        xlim=[0, 1.0],
        ylim=[0, 1.0],
        ylabel="True Positive Rate",
        xlabel="False Positive Rate",
    )
    ax.legend(loc="lower right")

    return mean_fpr, mean_tpr, mean_auc, std_auc


def plot_means(x1, y1, auc1, std1, x2, y2, auc2, std2):
    fig, ax = plt.subplots()

    ax.plot(
        [0, 1], [0, 1], linestyle="--", lw=2, color="grey", label="Chance", alpha=0.8
    )

    ax.plot(
        x1,
        y1,
        color="tab:blue",
        label=r"SVM (AUC = %0.2f $\pm$ %0.2f)" % (auc1, std1),
        lw=4,
    )

    ax.plot(
        x2,
        y2,
        color="tab:orange",
        label=r"TNKF-LSSVM (AUC = %0.2f $\pm$ %0.2f)" % (auc2, std2),
        lw=4,
    )

    # std_tpr = np.std(y1, axis=0)
    # tprs_upper = np.minimum(y1 + std1, 1)
    # tprs_lower = np.maximum(y1 - std1, 0)
    # ax.fill_between(
    #     x1,
    #     tprs_lower,
    #     tprs_upper,
    #     color="mediumblue",
    #     alpha=0.2,
    #     label="_nolegend-" #r"$\pm$ 1 std. dev.",
    # )

    # # std_tpr = np.std(y2, axis=0)
    # tprs_upper = np.minimum(y2 + std2, 1)
    # tprs_lower = np.maximum(y2 - std2, 0)
    # ax.fill_between(
    #     x2,
    #     tprs_lower,
    #     tprs_upper,
    #     color="firebrick",
    #     alpha=0.2,
    #     label="_nolegend_" #r"$\pm$ 1 std. dev.",
    # )

    ax.set(
        xlim=[0, 1.0],
        ylim=[0, 1.0],
        ylabel="True Positive Rate",
        xlabel="False Positive Rate",
        grid="on",
    )
    ax.legend(loc="lower right")

    return fig


N_data = 593
N_folds = 6

svm_predictions = []
svm_decision = []
tnkf_predictions = []
tnkf_decision = []

# Initialize ROC plot parameters
tprs_tnkf = []
aucs_tnkf = []
mean_fpr_tnkf = np.linspace(0, 1, 100)
fig_tnkf, ax_tnkf = plt.subplots()
# Initialize ROC plot parameters
tprs_svm = []
aucs_svm = []
mean_fpr_svm = np.linspace(0, 1, 100)
fig_svm, ax_svm = plt.subplots()
# true_labels = np.zeros((N_data, 1))

for i in range(0, N_folds):
    svm_results = pd.read_csv(
        SVM_PATH + "svm_results_fold_" + str(i) + ".csv", delimiter=","
    )
    tnkf_results = pd.read_csv(
        TNKF_PATH + "results_fold_" + str(i) + ".csv", delimiter=","
    )
    # Extract predictions
    svm_predictions.append(svm_results.loc[:, "predicted_labels"].to_numpy())
    svm_decision.append(svm_results.loc[:, "decision_function"].to_numpy())
    tnkf_predictions.append(tnkf_results.loc[:, "predicted_labels"].to_numpy())
    tnkf_decision.append(tnkf_results.loc[:, "decision_function"].to_numpy())
    # True labels
    true_labels = tnkf_results.loc[:, "true_labels"].to_numpy()
    true_labels[true_labels == 0] = 1
    # TNKF vizualization
    viz_tnkf = metrics.RocCurveDisplay.from_predictions(
        true_labels,
        tnkf_decision[i],
        name="fold {}".format(i),
        alpha=0.3,
        lw=1,
        ax=ax_tnkf,
    )
    interp_tpr = np.interp(mean_fpr_tnkf, viz_tnkf.fpr, viz_tnkf.tpr)
    interp_tpr[0] = 0.0
    tprs_tnkf.append(interp_tpr)
    aucs_tnkf.append(viz_tnkf.roc_auc)
    # SVM vizualization
    true_labels = svm_results.loc[:, "true_labels"].to_numpy()
    viz_svm = metrics.RocCurveDisplay.from_predictions(
        true_labels,
        svm_decision[i],
        name="fold {}".format(i),
        alpha=0.3,
        lw=1,
        ax=ax_svm,
    )
    interp_tpr = np.interp(mean_fpr_svm, viz_svm.fpr, viz_svm.tpr)
    interp_tpr[0] = 0.0
    tprs_svm.append(interp_tpr)
    aucs_svm.append(viz_svm.roc_auc)

x_mean_tnkf, y_mean_tnkf, auc_tnkf, std_tnkf = plot_additional_lines(
    ax_tnkf, tprs_tnkf, mean_fpr_tnkf, aucs_tnkf
)
x_mean_svm, y_mean_svm, auc_svm, std_svm = plot_additional_lines(
    ax_svm, tprs_svm, mean_fpr_svm, aucs_svm
)

fig_compare = plot_means(
    x_mean_svm,
    y_mean_svm,
    auc_svm,
    std_svm,
    x_mean_tnkf,
    y_mean_tnkf,
    auc_tnkf,
    std_tnkf,
)


# Save results
fig_tnkf.savefig(SVM_PATH + "roc_TNKF_SMOTE.pgf", format="pgf")
# fig_svm.savefig(SVM_PATH + "roc_SVM_SMOTE.pgf", format="pgf")
# fig_compare.savefig(SVM_PATH + "compare_rocs.pgf", format="pgf")
