from __future__ import print_function
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import sys
import time
import datetime
from src.utils.ulilz_MAIL import Dataset, gen_embeddings
from src.EN import EntityNetwork
from src.trainer.train import train
import numpy as np
import tensorflow as tf
import tflearn
import random
import docopt
import cPickle as pickle
import logging
from sklearn.grid_search import ParameterGrid


def get_parameters(data,epoch,sent_len,sent_numb,embedding_size, params):
    """
    create a random configuration from using dists to select random parameters
    :return: neural network parameters for create_model
    """
    #
    # embedding_file = 'data/glove.6B.{}d.txt'.format(embedding_size)
    # embeddings_mat = gen_embeddings(data._data['word_idx'], embedding_size, embedding_file)
    dists = dict(
    vocab_size = data._data["vocab_size"],label_num = data._data["vocab_size"],
    sent_len = sent_len, sent_numb = sent_numb, embedding_size = embedding_size,
    embeddings_mat = data._data['embeddings_mat'], clip_gradients= 40.0,
    max_norm = None, no_out = False, decay_steps = 0, decay_rate = 0, opt = params['op'],
    num_blocks = params['nb'],
    learning_rate= params['lr'],
    trainable = params['tr'],
    L2 = params['L2']
    )
    return dists

def main():
    embedding_size = 200
    epoch = 300
    best_accuracy = 0.0
    sent_numb,sent_len = None,None
    grind_ris={}

    param_grid = {'nb': [20,50],
                  'lr': [.01,0.001,0.0001],
                  'tr': [[1,1,0,0]],
                  'L2': [0.001,0.0001],
                  'bz': [64],
                  'dr': [0.5],
                  'mw': [150],
                  'w' : [3,4,5],
                  'op': ['Adam']
                  }
    grid = list(ParameterGrid(param_grid))
    np.random.shuffle(grid)
    for params in list(grid):

        data = Dataset(train_size=100000,dev_size=None,test_size=None,sent_len=sent_len,
                        sent_numb=sent_numb, embedding_size=embedding_size,
                        max_windows=params['mw'],win=params['w'])

        # ## for sentence
        # # par = get_parameters(data,epoch,sent_len,sent_numb,embedding_size)
        # ## for windows
        par = get_parameters(data,epoch,(params['w']*2)+1,params['mw'],embedding_size,params)

        t = train(epoch,params['bz'], data, par, dr=params['dr'], _test=False)

        acc = sorted([v for k,v in t[3].items()])[-1]

        if (acc > best_accuracy):
            best_accuracy = acc

        grind_ris[str(params)] = acc

        f_save = 'checkpoints/MAIL_WIND/{}.PIK'.format(str(params)+str(acc))
        with open(f_save, 'w') as f:
            pickle.dump((t), f)




if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m-%d %H:%M')
    main()
