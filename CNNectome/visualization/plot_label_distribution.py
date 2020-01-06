import json
import matplotlib.pyplot as plt
import matplotlib.font_manager
import numpy as np
from CNNectome.utils.label import Label

plt.rcParams["svg.fonttype"]= 'none'
def get_data(filename):
    with open(filename, "r") as f:
        stats = json.load(f)
    return stats

def rearrange(labels, stats):
    pos_counts = []
    for label in labels:
       # label = Label("a", 4)
        pos_counts.append(0)
        for lid in label.labelid:
            pos_counts[-1] += stats["positives"][str(lid)]
        print(label.labelname, pos_counts[-1]/5079502913)
    print(pos_counts)
    order = np.argsort(pos_counts)
    labelnames = [l.labelname for l in labels]
    #print(stats["negatives"]["3"]+stats["positives"]["3"])

    return [pos_counts], labelnames, order, ["positives"],[(102/255., 190/255., 121/255.),]



def get_raw_stats(stats):
    label_ids = sorted([int(k) for k in stats["positives"].keys()])
    pos_counts = [stats["positives"][str(lid)] / 8 for lid in label_ids]
    neg_counts = [stats["negatives"][str(lid)] / 8 for lid in label_ids]
    sum_counts = [stats["sums"][str(lid)] / 8 for lid in label_ids]
    order = np.argsort(pos_counts)
    label_names = ["ECS", "PM", "mito mem", "mito lum", "mito DNA", "golgi mem", "golgi lum", "vesicle mem",
                   "vesicle lum", "MVB mem", "MVB lum", "lysosome mem", "lysosome lum", "LD mem", "LD lum", "ER mem",
                   "ER lum", "ERES mem", "ERES lum", "NE mem", "NE lum", "nuc. pore out", "nuc. pore in", "HChrom",
                   "NHChrom", "EChrom", "NEChrom", "nucleoplasm", "nucleolus", "microtubules out", "centrosome",
                   "distal app", "subdistal app", "ribos", "microtubules in", "nucleus generic"]
    counts = [pos_counts, neg_counts]
    return counts, label_names, order, ["positives", "negatives"], [(102/255., 190/255.,
                                                                                             121/255.),(219/255.,
                                                                                                        47/255.,
                                                                                                        32/255.)]

def plot_hist(counts, label_names, order=None, count_labels = None, colors=None):
    plt.style.use('dark_background')
    fs = 40
    flist = matplotlib.font_manager.get_fontconfig_fonts()
    x = matplotlib.font_manager.findSystemFonts(fontpaths="groups/saalfeld/home/heinrichl/fonts/webfonts/",
                                               fontext="ttf")
    names = [matplotlib.font_manager.FontProperties(fname=fname).get_name() for fname in flist]
    plt.rcParams["font.family"]="Nimbus Sans L"

    #plt.rcParams["font.sans-serif"] = "NimbusSansL"
    #print([(l, s) for l, s in zip(label_ids,sum_counts)])
    fig, ax = plt.subplots(figsize=(40,25))

    x = np.arange(len(label_names))
    if order is None:
        order = list(range(len(label_names)))
    if count_labels is None:
        count_labels = [""]* len(counts)
    if colors is None:
        colors = [None,]* len(counts)
    width = 0.85/len(counts)
    # COLOR='white'
    # plt.rcParams['text.color'] = COLOR
    # plt.rcParams['axes.labelcolor'] = COLOR
    # plt.rcParams['xtick.color'] = COLOR
    # plt.rcParams['ytick.color'] = COLOR
    #plt.ylim([5*10**3, 0.8*10**9])
    plt.xlim([-2, x[-1]+2])

    for k, (c, l, col) in enumerate(zip(counts, count_labels, colors)):
        if col is not None:
            col_int = col + (100/255., )
            rects = ax.bar(x+k*width+0.01*k , np.array(c)[order], width, label=l, color=col_int, edgecolor=col)
        else:
            rects = ax.bar(x+k*width+0.01*k, np.array(c)[order], width, label=l)
            #(102/255.,190/255.,121/255.,100/255.), edgecolor = (102/255.,190/255.,121/255.))
    #rects2 = ax.bar(x + width/2, np.array(neg_counts)[order], width, label="labeled as negative", color=(219/255.,
     #                                                                                                  47/255.,
     #                                                                                      32/255., 100/255.),
      #              edgecolor = (219/255., 47/255., 32/255.))
    shift = (len(counts)*width+(len(counts)-1)*0.01)/2-width/2
    ax.set_xticks([xx+shift for xx in x])

    ax.set_xticklabels(np.array(label_names)[order], rotation=60, ha="right", fontsize=fs)
    #ax.set_yticklabels()
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(fs)
    plt.ylabel("# voxel", fontsize=fs)
    #print([(l, s) for l, s in zip(np.array(labelnames)[order], np.array(sum_counts)[order])])
    ax.legend(prop={'size': fs})
    #plt.semilogy()
    plt.tight_layout()
    #plt.savefig("/groups/saalfeld/home/heinrichl/figures/COSEM/organelle_distribution_both.svg")
    plt.show()

def main():
    #get_raw_stats(get_data("/groups/saalfeld/home/heinrichl/stats.json"))))
    #plot_hist(*get_raw_stats(get_data("/groups/saalfeld/home/heinrichl/stats.json")))
    labels = list()
    labels.append(Label("ecs", 1))
    labels.append(Label("blobs", (3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)))
    labels.append(Label("membranes", (2,3,6,8,10,12,14,16,18,20,22)))
    labels.append(Label("nucleus", (20,21,22,23,24,25,26,27,28,29,37), generic_label=37))

    plot_hist(*rearrange(labels, get_data("/groups/saalfeld/home/heinrichl/stats.json")))

if __name__ == "__main__":
    main()
