from models import GCN, GAT, CNN, train, eval
import dataset_loader as dsl

import numpy as np
import torch
from torch.utils.data import ConcatDataset, SubsetRandomSampler, Subset
from torch_geometric.loader import DataLoader

from sklearn.model_selection import StratifiedKFold, train_test_split

def checkpoint(model, directory, filename):
    file = directory + filename +  '.pth'
    torch.save(model.state_dict(), file)

if __name__ == '__main__':
    import argparse
    import csv
    import time
    import os

    torch.manual_seed(42)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", "-m", type=str, default="GCN", 
                        help="the model to train: GCN, GAT or CNN. default = GCN")
    parser.add_argument("--epochs", "-e", type=int, default=100,
                        help="max number of training epochs")
    parser.add_argument("--learning_rate", "-lr", type=float, default=0.001,
                        help="learning rate")
    parser.add_argument("--patience", type=int, default=5,
                        help="allowed epochs without min. improvement berfore early stopping. default = 5")
    parser.add_argument("--min_improvement", type=float, default=0.01,
                        help="min improvement from previous epoch. default = 0.01")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--n_heads", type=int, default=2, 
                        help='number of attention heads in GAT layer. default = 2')
    parser.add_argument('--n_layers', type=int, default=3, 
                        help='number of stacked conv. layers (GAT or GCN). default = 3')
    parser = dsl.set_dataset_arguments(parser)
    args = parser.parse_args()

    field_names = ["epoch", 
                   "accuracy", 
                   "precision (micro)", "precision (macro)", "precision (weighted)", 
                   "recall (micro)", "recall (macro)", "recall (weighted)", 
                   "f-measure (micro)", "f-measure (macro)", "f-measure (weighted)", 
                   "loss", "validation loss"]
    meta_field_names = ['model',
                        'num. layers',
                        'num. heads',
                        'stopped-at',
                        'n_segments', 
                        'compactness', 
                        'graph type', 
                        'slic method',
                        'features', 
                        'avg. num. of nodes', 
                        'std. dev. of num. of nodes', 
                        'avg. num. of edges', 
                        'std. dev. of num. of edges', 
                        'best epochs',
                        'last epochs',
                        'accuracy', 
                        'precision micro',
                        'precision macro',
                        'precision weighted',
                        'recall micro',
                        'recall macro',
                        'recall weighted',
                        'micro', 
                        'macro',
                        'weighted', 
                        'avg. loss', 
                        'training time',
                        'loading time']
    t0 = time.time()
    ds, splits, labels = dsl.load_dataset(args)
    loading_time = time.time() - t0
    ds_info = dsl.dataset_info(args)

    meta_info = {}
    info_ds = ds.datasets[0]
    meta_info['model'] = args.model
    meta_info['loading time'] = loading_time
    if args.model != 'CNN':
        meta_info['num. layers'] = args.n_layers
        if args.model == 'GAT':
            meta_info['num. heads'] = args.n_heads
        else:
            meta_info['num. heads'] = '-' 
        meta_info['avg. num. of nodes'] = info_ds.avg_num_nodes
        meta_info['std. dev. of num. of nodes'] = info_ds.std_deviation_num_nodes
        meta_info['avg. num. of edges'] = info_ds.avg_num_edges
        meta_info['std. dev. of num. of edges'] = info_ds.std_deviation_num_edges
        meta_info['n_segments']  = info_ds.n_segments
        meta_info['graph type'] =  info_ds.graph_type
        meta_info['slic method'] = info_ds.slic_method
        meta_info['features'] = ' '.join(info_ds.features)
        if info_ds.slic_method == 'SLIC':
            meta_info['compactness'] = info_ds.compactness
        else:
            meta_info['compactness'] = '-'
    else:
        meta_info['num. layers'] = 3
        meta_info['num. heads'] = '-' 
        meta_info['avg. num. of nodes'] = '-'
        meta_info['std. dev. of num. of nodes'] = '-'
        meta_info['avg. num. of edges'] = '-'
        meta_info['std. dev. of num. of edges'] = '-'
        meta_info['n_segments']  = '-'
        meta_info['compactness'] = '-'
        meta_info['graph type'] = '-'
        meta_info['slic method'] = '-'
        meta_info['features'] = '-'
    
    out_dir = f'./{args.model}/{args.dataset}/'
    if args.model == 'CNN':
        out_file = 'cnn'
    elif args.model == 'GAT':
        out_file = 'l{}h{}n{}-{}-{}-{}'.format(args.n_layers, 
                                                   args.n_heads, 
                                                   info_ds.n_segments,
                                                   info_ds.graph_type,
                                                   info_ds.slic_method if info_ds.slic_method == 'SLIC0' else info_ds.slic_method + 'c' + str(info_ds.compactness),
                                                   '-'.join(info_ds.features))
    else:
        out_file = 'l{}n{}-{}-{}-{}'.format(args.n_layers, 
                                                info_ds.n_segments,
                                                info_ds.graph_type,
                                                info_ds.slic_method if info_ds.slic_method == 'SLIC0' else info_ds.slic_method + 'c' + str(info_ds.compactness),
                                                '-'.join(info_ds.features))


    meta_out = './{}_training_info.csv'.format(args.dataset)

    os.makedirs(out_dir, exist_ok=True)
    with open(out_dir + out_file + '.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(device)
    
    epochs = args.epochs
    verbose_output = args.verbose
    patience = args.patience
    min_improvement = args.min_improvement 

    history = []
    training_time = []
    last_epochs = []
    best_epochs = []

    # stratified k-fold cross validation 
    for train_index, test_index in splits:
        # test data 
        test_loader  = DataLoader(ds, batch_size=64, sampler=SubsetRandomSampler(test_index))
        
        # train data divided into 10% validation and 90% train, maintaning class proportions 
        train_index, validation_index = train_test_split(Subset(ds, train_index), test_size=0.1, stratify=Subset(labels, train_index))
        train_loader = DataLoader(ds, batch_size=64, sampler=SubsetRandomSampler(train_index))
        validation_loader = DataLoader(ds, batch_size=64, sampler=SubsetRandomSampler(validation_index))

        if args.model == 'GCN':
            model = GCN(info_ds.num_features, ds_info['classes'], args.n_layers).to(device)
            optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
            loss_fn = torch.nn.CrossEntropyLoss()
        elif args.model == 'GAT':
            model = GAT(info_ds.num_features, ds_info['classes'], args.n_heads, args.n_layers).to(device)
            optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
            loss_fn = torch.nn.CrossEntropyLoss()
        elif args.model == CNN:
            model = CNN(ds_info['channels'], ds_info['classes'], ds_info['img_size']).to(device)
            optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
            loss_fn = torch.nn.CrossEntropyLoss()
        else:
            print(f"No dataset named \"{args.dataset}\" available.")

        fold_hist = []
        epochs_without_improvement = 0
        previous_validation_res = {}
        best_validation_res = {}
        best_epoch = 0
        last_epoch = 0
        print('------------------------')
        print(f'FOLD {len(history) + 1}/{5}')
        t0 = time.time()
        for t in range(epochs):
            # 1. train model 
            train(train_loader, model, loss_fn, optimizer, device)

            # 2. evaluate model with validation set, checking if model should stop 
            #    and keeping track of the best epoch so far 
            validation_res = eval(validation_loader, model, loss_fn, device, labels)
            if t > 0:
                if validation_res['loss'] - previous_validation_res['loss'] < min_improvement:
                    epochs_without_improvement += 1
                if validation_res['loss'] < best_validation_res['loss']:
                    best_validation_res = validation_res
                    best_epoch = t
                    checkpoint(model, out_dir, out_file)
            else:
                best_validation_res = validation_res
                best_epoch = t
                checkpoint(model, out_dir, out_file)
            
            # 3. evaluate model with test set, reporting performance metrics 
            test_res = eval(test_loader, model, loss_fn, device, labels)
            test_res['epoch'] = t
            test_res['validation loss'] = validation_res['loss']
            if verbose_output:
                print(f'Epoch: {t}, f1: {test_res["f1-measure (macro)"]}, loss: {test_res["loss"]}')
            fold_hist.append(test_res)

            # early stop
            if epochs_without_improvement > patience:
                print(f'Stopped at epoch {t}')
                break

        tf = time.time()
        print(f"Done in {tf - t0}s. F-measure {fold_hist[-1]['f1-measure (macro)']}")
        training_time.append(tf - t0)
        history.append(fold_hist)
        last_epochs.append(str(fold_hist[-1]['epoch']))
        best_epochs.append(str(best_epoch))

    avg_res = {}
    with open(out_dir + out_file + '.csv', 'a', newline='') as csvfile:
        history = np.array(history)
        for e in range(epochs):
            for field in field_names:
                avg_res[field] = np.average([f[field] for f in history[:,e]])
                if np.isnan(avg_res[field]):
                    avg_res[field] = '-'
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writerow(avg_res)

    meta_info['training time'] = np.average(training_time)
    meta_info['accuracy'] = avg_res['Accuracy']
    meta_info['precision micro'] = avg_res['Precision (micro)']
    meta_info['precision macro'] = avg_res['Precision (macro)']
    meta_info['precision weighted'] = avg_res['Precision (weighted)']
    meta_info['recall micro'] = avg_res['Recall (micro)']
    meta_info['recall macro'] = avg_res['Recall (macro)']
    meta_info['recall weighted'] = avg_res['Recall (weighted)']
    meta_info['micro'] = avg_res['F-measure (micro)']
    meta_info['macro'] = avg_res['F-measure (macro)']
    meta_info['weighted'] = avg_res['F-measure (weighted)']
    meta_info['avg. loss'] = avg_res['Avg loss']
    meta_info['last epochs'] = ', '.join(last_epochs)
    meta_info['best epochs'] = ', '.join(best_epochs)
    
    with open(meta_out, 'a', newline='') as infofile:
        writer = csv.DictWriter(infofile, fieldnames=meta_field_names)
        writer.writerow(meta_info)