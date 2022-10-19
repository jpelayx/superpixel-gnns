from grayscale_slic import GrayscaleSLIC

import torchvision.datasets as datasets 
import torchvision.transforms as T

class SuperPixelGraphFashionMNIST(GrayscaleSLIC):
    ds_name = 'FashionMNIST'
    def get_ds_name(self):
        self.features.sort()
        return  './fashion_mnist/{}-n{}-c{}-{}'.format('train' if self.train else 'test', 
                                                 self.n_segments, 
                                                 self.compactness,
                                                 '-'.join(self.features))
    def get_labels(self):
        return list(range(10))
    def load_data(self):
        mnist_root = './fashion_mnist/{}'.format('train' if self.train else 'test')
        return datasets.FashionMNIST(mnist_root, train=self.train, download=True, transform=T.ToTensor())
