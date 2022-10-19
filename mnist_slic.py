from grayscale_slic import GrayscaleSLIC

import torchvision.datasets as datasets 
import torchvision.transforms as T

class SuperPixelGraphMNIST(GrayscaleSLIC):
    ds_name = 'MNIST'
    def get_ds_name(self):
        self.features.sort()
        return  './mnist/{}-n{}-c{}-{}'.format('train' if self.train else 'test', 
                                                 self.n_segments, 
                                                 self.compactness,
                                                 '-'.join(self.features))
    def load_data(self):
        mnist_root = './mnist/{}'.format('train' if self.train else 'test')
        return datasets.MNIST(mnist_root, train=self.train, download=True, transform=T.ToTensor())

