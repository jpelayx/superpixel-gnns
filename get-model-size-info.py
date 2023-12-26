import torch 
import numpy as np

import csv 

if __name__ == '__main__':

    dss = [
        'mnist', 
        'fashion_mnist', 
        'cifar10',
        'cifar100',
        'stl10'
    ]

    ids = ['best model']
    basedir = 'GCN'
    model_paths = {
        'mnist': ['l3n50-RAG-SLIC0-avg_color-centroid-num_pixels-std_deviation_centroid-std_deviation_color'],
        'fashion_mnist': ['l3n200-1NNFeature-SLIC0-avg_color-centroid-num_pixels-std_deviation_centroid-std_deviation_color'],
        'cifar10': ['l3n400-1NNFeature-SLIC0-avg_color-avg_color_hsv-centroid-num_pixels-std_deviation_centroid-std_deviation_color-std_deviation_color_hsv'],
        'cifar100': ['l3n200-1NNFeature-SLIC0-avg_color-avg_color_hsv-centroid-std_deviation_centroid-std_deviation_color-std_deviation_color_hsv'],
        'stl10': ['l3n400-2NNFeature-SLIC0-avg_color-avg_color_hsv-centroid-std_deviation_centroid-std_deviation_color']
    }

    out_fields = [
        'model', 
        'model size'
    ]


    for ds in dss:
        out_file = basedir + f'/{ds}-comparisons-modelsizeinfo.csv'
        with open(out_file, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=out_fields)
            writer.writeheader()
        sizes = []
        print(ds)
        for id, path in enumerate(model_paths[ds]):
            print('Filename: ', path)
            fold_sizes = []
            for f in range(5):
                model_path = basedir + f'/{ds}/' + path + f'.fold{f}.pth'
                model = torch.load(model_path)
                fold_size = 0
                for layer in model:
                    layer_size = np.prod(model[layer].shape) * model[layer].element_size()
                    fold_size += layer_size
                fold_sizes.append(fold_size)
            mean_size = np.mean(fold_sizes)
            sizes.append(mean_size)
            print(ids[id], mean_size)
            with open(out_file, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=out_fields)
                writer.writerow({out_fields[0] : ids[id], out_fields[1] : mean_size})

        



