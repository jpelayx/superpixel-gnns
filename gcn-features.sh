#!/bin/sh
python3 train-model.py --dataset mnist -f GCN/mnist-features --features "avg_color"
python3 train-model.py --dataset mnist -f GCN/mnist-features --features "avg_color centroid"
python3 train-model.py --dataset mnist -f GCN/mnist-features --features "avg_color centroid std_deviation_color"
python3 train-model.py --dataset mnist -f GCN/mnist-features --features "avg_color centroid std_deviation_color num_pixels"
python3 train-model.py --dataset mnist -f GCN/mnist-features --features "avg_color centroid std_deviation_color std_deviation_centroid"

python3 train-model.py --dataset fashion_mnist -f GCN/fashion_mnist-features --features "avg_color"
python3 train-model.py --dataset fashion_mnist -f GCN/fashion_mnist-features --features "avg_color centroid"
python3 train-model.py --dataset fashion_mnist -f GCN/fashion_mnist-features --features "avg_color centroid std_deviation_color"
python3 train-model.py --dataset fashion_mnist -f GCN/fashion_mnist-features --features "avg_color centroid std_deviation_color num_pixels"
python3 train-model.py --dataset fashion_mnist -f GCN/fashion_mnist-features --features "avg_color centroid std_deviation_color std_deviation_centroid"

python3 train-model.py --dataset cifar10 -f GCN/cifar10-features --features "avg_color"
python3 train-model.py --dataset cifar10 -f GCN/cifar10-features --features "avg_color centroid"
python3 train-model.py --dataset cifar10 -f GCN/cifar10-features --features "avg_color centroid std_deviation_color"
python3 train-model.py --dataset cifar10 -f GCN/cifar10-features --features "avg_color centroid std_deviation_color num_pixels"
python3 train-model.py --dataset cifar10 -f GCN/cifar10-features --features "avg_color centroid std_deviation_color std_deviation_centroid"
python3 train-model.py --dataset cifar10 -f GCN/cifar10-features --features "avg_color centroid std_deviation_color std_deviation_centroid avg_color_hsv"
python3 train-model.py --dataset cifar10 -f GCN/cifar10-features --features "avg_color centroid std_deviation_color std_deviation_centroid avg_color_hsv std_deviation_color_hsv"

python3 train-model.py --dataset cifar100 -f GCN/cifar100-features --features "avg_color"
python3 train-model.py --dataset cifar100 -f GCN/cifar100-features --features "avg_color centroid"
python3 train-model.py --dataset cifar100 -f GCN/cifar100-features --features "avg_color centroid std_deviation_color"
python3 train-model.py --dataset cifar100 -f GCN/cifar100-features --features "avg_color centroid std_deviation_color num_pixels"
python3 train-model.py --dataset cifar100 -f GCN/cifar100-features --features "avg_color centroid std_deviation_color std_deviation_centroid"
python3 train-model.py --dataset cifar100 -f GCN/cifar100-features --features "avg_color centroid std_deviation_color std_deviation_centroid avg_color_hsv"
python3 train-model.py --dataset cifar100 -f GCN/cifar100-features --features "avg_color centroid std_deviation_color std_deviation_centroid avg_color_hsv std_deviation_color_hsv"

python3 train-model.py --dataset stl10 -f GCN/stl10-features --features "avg_color"
python3 train-model.py --dataset stl10 -f GCN/stl10-features --features "avg_color centroid"
python3 train-model.py --dataset stl10 -f GCN/stl10-features --features "avg_color centroid std_deviation_color"
python3 train-model.py --dataset stl10 -f GCN/stl10-features --features "avg_color centroid std_deviation_color num_pixels"
python3 train-model.py --dataset stl10 -f GCN/stl10-features --features "avg_color centroid std_deviation_color std_deviation_centroid"
python3 train-model.py --dataset stl10 -f GCN/stl10-features --features "avg_color centroid std_deviation_color std_deviation_centroid avg_color_hsv"
python3 train-model.py --dataset stl10 -f GCN/stl10-features --features "avg_color centroid std_deviation_color std_deviation_centroid avg_color_hsv std_deviation_color_hsv"
