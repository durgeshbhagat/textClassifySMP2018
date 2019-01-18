import data_utils
from training_utils import convert_y
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "7"
from keras.layers import Input, Embedding, Conv1D, Dense, GlobalMaxPool1D, GlobalAveragePooling1D, Concatenate
from keras.layers import BatchNormalization
from keras import Model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from keras.optimizers import SGD, Adam, Adagrad
import numpy as np
import random
from data_utils import TrainConfigure, ValidConfigure
from hybridmodel import HybridModel
from charmodel import CharModel
from attmodel import AttModel
from termmodel import TermModel
from deepcnn import DeepCNNModel
from conditionmodel import ConditionModel
from gatedconvmodel import GatedConvModel
from gateddeepcnn import GatedDeepCNNModel
from sscharmodel import SSCharModel
from gatedconvtopicmodel import GatedConvTopicModel
from RCNNmodel import RCNNModel
import fasttextmodel
from hybridattmodel import HybridAttModel
from hybridconvmodel import HybridConvModel
from hybriddpcnnmodel import HybridDPCNNModel
from hybridgateddeepcnnmodel import HybridGatedDeepCNNModel
from hybridRCNNmodel import HybridRCNNModel
from hybridgatedconvmodel import HybridGatedConvTopicModel

from conditionattmodel import ConditionAttModel
from conditionconvmodel import ConditionConvModel
from conditiondpcnnmodel import ConditionDPCNNModel
from conditiongatedconvmodel import ConditionGatedConvModel
from conditiongateddeepcnnmodel import ConditionGatedDeepCNNModel
from conditionRCNNmodel import ConditionRCNNModel
from hybridsenetwork import HybridSEModel
from hybriddensemodel import HybridDenseModel
from hybriddensemamodel import HybridDenseMAModel

def predict_all():
    """
    根据概率集成
    :return:
    """
    print('load data')
    tn_conf = TrainConfigure()
    data_dict = data_utils.pickle_load(tn_conf.char_file)
    y = to_categorical(data_dict['y'])
    x = data_dict['x']
    xterm = data_utils.pickle_load(tn_conf.term_file)
    xfeat = data_utils.pickle_load(tn_conf.feat_file)
    # normalization
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    scaler.fit(xfeat)
    data_utils.pickle_dump(scaler, tn_conf.feat_norm)
    xfeat = scaler.transform(xfeat)
    xe = [[i for i in range(600)] for _ in range(y.shape[0])]
    xe = np.array(xe)
    xe_term = [[i for i in range(300)] for _ in range(y.shape[0])]
    xe_term = np.array(xe_term)

    xtopic = data_utils.pickle_load('data/lda_vec_val.pkl')

    print('loading embed ...')
    term_vocab_dict = data_utils.pickle_load(tn_conf.term_dict)
    term_embed_matrix = data_utils.load_embedding(term_vocab_dict,
                                                  'data/sgns.target.word-character.char1-2.dynwin5.thr10.neg5.dim300.iter5',
                                                  dump_path='data/term_embed.pkl')
    # term_embed_matrix = data_utils.load_embedding(term_vocab_dict,
    #                                               'data/sgns.target.word-word.dynwin5.thr10.neg5.dim300.iter5',
    #                                               dump_path='data/term_embed_ww.pkl')
    char_vocab_dict = data_utils.pickle_load(tn_conf.char_dict)
    char_embed_matrix = data_utils.load_embedding(char_vocab_dict,
                                                  'data/sgns.target.word-character.char1-2.dynwin5.thr10.neg5.dim300.iter5',
                                                  dump_path='data/char_embed.pkl')
    print('load embed done.')
    val_conf = ValidConfigure()
    data_dict = data_utils.pickle_load(val_conf.char_file)
    y = to_categorical(data_dict['y'])
    x = data_dict['x']
    ids = data_dict['id']
    xterm = data_utils.pickle_load(val_conf.term_file)
    xfeat = data_utils.pickle_load(val_conf.feat_file)
    xfeat = scaler.transform(xfeat)
    print('feat shape', xfeat.shape)


    import data_utils100
    val_conf100 = data_utils100.ValidConfigure()
    data_dict100 = data_utils.pickle_load(val_conf100.char_file)
    x100 = data_dict100['x']
    xterm100 = data_utils.pickle_load(val_conf100.term_file)
    xe100 = [[i for i in range(100)] for _ in range(y.shape[0])]
    xe100 = np.array(xe100)
    xe_term100 = [[i for i in range(100)] for _ in range(y.shape[0])]
    xe_term100 = np.array(xe_term100)

    import data_utils200
    val_conf200 = data_utils200.ValidConfigure()
    data_dict200 = data_utils.pickle_load(val_conf200.char_file)
    x200 = data_dict200['x']
    xterm200 = data_utils.pickle_load(val_conf200.term_file)
    xe200 = [[i for i in range(200)] for _ in range(y.shape[0])]
    xe200 = np.array(xe200)
    xe_term200 = [[i for i in range(200)] for _ in range(y.shape[0])]
    xe_term200 = np.array(xe_term200)

    ys = []
    print('define model')
    model = HybridDenseModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                            PE=True, name='hybriddensemodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model

    model = HybridDenseMAModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                            PE=True, name='hybriddensemodelma_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('dense model done.')

    model = HybridSEModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                            PE=True, name='hybridsemodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('se model done.')

    print('start len 100 model')
    model = HybridConvModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, MAX_LEN=100, MAX_LEN_TERM=100,NUM_FEAT=8,
                            PE=True, name='hybridconvmodel_n100.h5')
    model.load_weights()
    y = model.predict([x100, xe100, xterm100, xe_term100, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid conv model done.')

    # model = HybridDPCNNModel(char_embed_matrix=char_embed_matrix,
    #                          term_embed_matrix=term_embed_matrix, MAX_LEN=100, MAX_LEN_TERM=100,NUM_FEAT=8,
    #                          PE=True, name='hybriddpcnnmodel_n100.h5')
    # model.load_weights()
    # y = model.predict([x100, xe100, xterm100, xe_term100, xfeat, xtopic])
    # ys.append(y)
    # del model
    # print('hybrid dpcnn model done.')

    model = HybridGatedDeepCNNModel(char_embed_matrix=char_embed_matrix,
                                    term_embed_matrix=term_embed_matrix, MAX_LEN=100, MAX_LEN_TERM=100,NUM_FEAT=8,
                                    PE=True, name='hybridgateddeepcnnmodel_n100.h5')
    model.load_weights()
    y = model.predict([x100, xe100, xterm100, xe_term100, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid gated deep cnn model done.')

    model = HybridRCNNModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, MAX_LEN=100, MAX_LEN_TERM=100,NUM_FEAT=8,
                            PE=True, name='hybridrcnnmodel_n100.h5')
    model.load_weights()
    y = model.predict([x100, xe100, xterm100, xe_term100, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid RCNN model done.')

    # print('start len 200 model')
    # model = HybridConvModel(char_embed_matrix=char_embed_matrix,
    #                         term_embed_matrix=term_embed_matrix, MAX_LEN=200, MAX_LEN_TERM=200,NUM_FEAT=8,
    #                         PE=True, name='hybridconvmodel_n200.h5')
    # model.load_weights()
    # y = model.predict([x200, xe200, xterm200, xe_term200, xfeat, xtopic])
    # ys.append(y)
    # del model
    # print('hybrid conv model done.')
    #
    # model = HybridDPCNNModel(char_embed_matrix=char_embed_matrix,
    #                          term_embed_matrix=term_embed_matrix, MAX_LEN=200, MAX_LEN_TERM=200,NUM_FEAT=8,
    #                          PE=True, name='hybriddpcnnmodel_n200.h5')
    # model.load_weights()
    # y = model.predict([x200, xe200, xterm200, xe_term200, xfeat, xtopic])
    # ys.append(y)
    # del model
    # print('hybrid dpcnn model done.')
    #
    # model = HybridGatedDeepCNNModel(char_embed_matrix=char_embed_matrix,
    #                                 term_embed_matrix=term_embed_matrix, MAX_LEN=200, MAX_LEN_TERM=200,NUM_FEAT=8,
    #                                 PE=True, name='hybridgateddeepcnnmodel_n200.h5')
    # model.load_weights()
    # y = model.predict([x200, xe200, xterm200, xe_term200, xfeat, xtopic])
    # ys.append(y)
    # del model
    # print('hybrid gated deep cnn model done.')
    #
    # model = HybridRCNNModel(char_embed_matrix=char_embed_matrix,
    #                         term_embed_matrix=term_embed_matrix, MAX_LEN=200, MAX_LEN_TERM=200,NUM_FEAT=8,
    #                         PE=True, name='hybridrcnnmodel_n200.h5')
    # model.load_weights()
    # y = model.predict([x200, xe200, xterm200, xe_term200, xfeat, xtopic])
    # ys.append(y)
    # del model

    #这个模型太慢
    # model = ConditionAttModel(char_embed_matrix=char_embed_matrix,
    #                           term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
    #                           name='conditionattmodel_PE.h5', lr=0.001)
    # model.load_weights()
    # y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    # ys.append(y)
    # print('condition att model done.')

    model = ConditionConvModel(char_embed_matrix=char_embed_matrix,
                              term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
                              name='conditionconvmodel_PE.h5', lr=0.001)
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('condition conv model done.')

    model = ConditionDPCNNModel(char_embed_matrix=char_embed_matrix,
                               term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
                               name='conditiondpcnnmodel_PE.h5', lr=0.001)
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('condition dpcnn model done.')

    model = ConditionGatedConvModel(char_embed_matrix=char_embed_matrix,
                                term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
                                name='conditiongatedconvmodel_PE.h5', lr=0.001)
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('condition gated conv model done.')

    model = ConditionGatedDeepCNNModel(char_embed_matrix=char_embed_matrix,
                                    term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
                                    name='conditiongateddeepcnnmodel_PE.h5', lr=0.001)
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('condition gated deepcnn model done.')

    #这个模型太慢
    # model = ConditionRCNNModel(char_embed_matrix=char_embed_matrix,
    #                                    term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
    #                                    name='conditionrcnnmodel_PE.h5', lr=0.001)
    # model.load_weights()
    # y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    # ys.append(y)
    # print('condition rcnn model done.')


    model = HybridAttModel(char_embed_matrix=char_embed_matrix,
                                      term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                                      PE=True, name = 'hybridattmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)

    model = HybridAttModel(char_embed_matrix=char_embed_matrix,
                                      term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                                      name='hybridattmodel.h5')
    model.load_weights()
    y = model.predict([x, xterm, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid att model done.')

    model = HybridConvModel(char_embed_matrix=char_embed_matrix,
                           term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                           PE=True, name='hybridconvmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model

    model = HybridConvModel(char_embed_matrix=char_embed_matrix,
                           term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                           name='hybridconvmodel.h5')
    model.load_weights()
    y = model.predict([x, xterm, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid conv model done.')

    model = HybridDPCNNModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                            PE=True, name='hybriddpcnnmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model

    model = HybridDPCNNModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                            name='hybriddpcnnmodel.h5')
    model.load_weights()
    y = model.predict([x, xterm, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid dpcnn model done.')

    model = HybridGatedDeepCNNModel(char_embed_matrix=char_embed_matrix,
                             term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                             PE=True, name='hybridgateddeepcnnmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model

    model = HybridGatedDeepCNNModel(char_embed_matrix=char_embed_matrix,
                             term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                             name='hybridgateddeepcnnmodel.h5')
    model.load_weights()
    y = model.predict([x, xterm, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid gated deep cnn model done.')

    model = HybridRCNNModel(char_embed_matrix=char_embed_matrix,
                                    term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                                    PE=True, name='hybridrcnnmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model

    model = HybridRCNNModel(char_embed_matrix=char_embed_matrix,
                                    term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                                    name='hybridrcnnmodel.h5')
    model.load_weights()
    y = model.predict([x, xterm, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid rcnn model done.')

    model = ConditionModel(embed_matrix=char_embed_matrix)
    model.load_weights( )
    y = model.predict(x)
    ys.append(y)

    model = ConditionModel(embed_matrix=char_embed_matrix, PE=True, name='conditionmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe])
    ys.append(y)
    del model

    model = ConditionModel(embed_matrix=term_embed_matrix, MAX_LEN=300, name='conditionmodel_term.h5')
    model.load_weights()
    y = model.predict(xterm)
    ys.append(y)

    model = ConditionModel(embed_matrix=term_embed_matrix, MAX_LEN=300, PE=True, name='conditionmodel_term_PE.h5')
    model.load_weights()
    y = model.predict([xterm, xe_term])
    ys.append(y)
    del model
    print('condition model done.')


    model = GatedConvTopicModel(embed_matrix=char_embed_matrix, PE=True, name = 'gatedconvtopicmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xtopic])
    ys.append(y)
    print('gated conv topic done.')

    model = HybridGatedConvTopicModel(char_embed_matrix=char_embed_matrix,
                                      term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                                      PE=True, name='hybridgatedconvtopicmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)

    model = HybridGatedConvTopicModel(char_embed_matrix=char_embed_matrix,
                                      term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                                      name='hybridgatedconvtopicmodel.h5')
    model.load_weights()
    y = model.predict([x, xterm, xfeat, xtopic])
    ys.append(y)
    print('hybrid gated conv topic done.')

    model = RCNNModel(MAX_LEN=300, embed_matrix=term_embed_matrix, name='RCNNmodel.h5')
    model.load_weights()
    y = model.predict(xterm)
    ys.append(y)
    print('RCNN done.')

    y = fasttextmodel.predict_char()
    ys.append(y)

    y = fasttextmodel.predict_term()
    ys.append(y)
    print(y.shape)
    print('fast text done.')

    #hybrid model
    model = HybridModel(char_embed_matrix=char_embed_matrix, term_embed_matrix=term_embed_matrix, NUM_FEAT=8)# + 37
    model.load_weights()
    y = model.predict([x, xterm, xfeat])
    ys.append( y )
    print(y.shape)
    print('hybrid model done.')
    #CNN model (char)
    model = CharModel(embed_matrix=char_embed_matrix)
    model.load_weights()
    y = model.predict(x)
    ys.append(y)

    model = CharModel(embed_matrix=char_embed_matrix, name='charmodel_PE.h5', PE=True)
    model.load_weights()
    y = model.predict([x, xe])
    ys.append(y)

    model = CharModel(embed_matrix=char_embed_matrix, name='charmodel_PE_OE.h5', PE=True)
    model.load_weights()
    y = model.predict([x, xe])
    ys.append(y)

    print('char model done.')

    #CNN (term)
    model = TermModel(embed_matrix=term_embed_matrix)
    model.load_weights()
    y = model.predict(xterm)
    ys.append(y)
    print('term model done.')

    model = DeepCNNModel(embed_matrix=char_embed_matrix)
    model.load_weights()
    y = model.predict(x)
    ys.append(y)
    print('deep cnn done.')
    # attention model (char)
    model = AttModel(MAX_LEN=600, name='charattmodel.h5', embed_matrix=char_embed_matrix)
    model.load_weights()
    y = model.predict(x)
    ys.append(y)
    print('att char done.')

    # attention model (term)
    model = AttModel(MAX_LEN=300, embed_matrix=term_embed_matrix)
    model.load_weights()
    y = model.predict(xterm)
    ys.append(y)
    print('att term done.')

    model = SSCharModel(embed_matrix=char_embed_matrix, name='sscharmodel_PE.h5', PE=True, train_embed=True)
    model.load_weights()
    y = model.predict([x, xe])
    ys.append(y)

    model = SSCharModel(embed_matrix=char_embed_matrix, train_embed=True)
    model.load_weights()
    y = model.predict(x)
    ys.append(y)
    print('conv model with second learning passes done.')

    model = GatedConvModel(embed_matrix=char_embed_matrix, name='gatedconvmodel_PE.h5', PE=True)
    model.load_weights()
    y = model.predict([x, xe])
    ys.append(convert_onehot(y))

    model = GatedConvModel(embed_matrix=char_embed_matrix, train_embed=True)
    model.load_weights()
    y = model.predict(x)
    ys.append(y)
    print('gated conv done.')

    model = GatedDeepCNNModel(embed_matrix=char_embed_matrix, name='gateddeepcnnmodel_PE.h5', PE=True, train_embed=True)
    model.load_weights()
    y = model.predict([x, xe])
    ys.append(y)

    model = GatedDeepCNNModel(embed_matrix=char_embed_matrix, train_embed=True)
    model.load_weights()
    y = model.predict(x)
    ys.append(y)
    print('gated deep cnn done.')


    labels = ['人类作者', '自动摘要', '机器作者', '机器翻译']
    y_pred = np.mean(ys, axis=0)
    y_pred = convert_y(y_pred)
    out_file = 'result.csv'
    with open(out_file, 'w', encoding='utf-8') as fout:
        for id, yi in zip(ids, y_pred):
            label = labels[yi]
            fout.write('{},{}\n'.format(id, label))
    print('done.')

def predict(tn_conf, lda_file, val_conf, val_conf100, val_conf200):
    """
    根据概率集成
    :return:
    """
    print('load data')
    data_dict = data_utils.pickle_load(tn_conf.char_file)
    y = to_categorical(data_dict['y'])
    x = data_dict['x']
    xterm = data_utils.pickle_load(tn_conf.term_file)
    xfeat = data_utils.pickle_load(tn_conf.feat_file)
    # normalization
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    scaler.fit(xfeat)
    data_utils.pickle_dump(scaler, tn_conf.feat_norm)
    xfeat = scaler.transform(xfeat)
    xe = [[i for i in range(600)] for _ in range(y.shape[0])]
    xe = np.array(xe)
    xe_term = [[i for i in range(300)] for _ in range(y.shape[0])]
    xe_term = np.array(xe_term)

    xtopic = data_utils.pickle_load(lda_file)

    print('loading embed ...')
    term_vocab_dict = data_utils.pickle_load(tn_conf.term_dict)
    term_embed_matrix = data_utils.load_embedding(term_vocab_dict,
                                                  'data/sgns.target.word-character.char1-2.dynwin5.thr10.neg5.dim300.iter5',
                                                  dump_path='data/term_embed.pkl')
    # term_embed_matrix = data_utils.load_embedding(term_vocab_dict,
    #                                               'data/sgns.target.word-word.dynwin5.thr10.neg5.dim300.iter5',
    #                                               dump_path='data/term_embed_ww.pkl')
    char_vocab_dict = data_utils.pickle_load(tn_conf.char_dict)
    char_embed_matrix = data_utils.load_embedding(char_vocab_dict,
                                                  'data/sgns.target.word-character.char1-2.dynwin5.thr10.neg5.dim300.iter5',
                                                  dump_path='data/char_embed.pkl')
    print('load embed done.')
    data_dict = data_utils.pickle_load(val_conf.char_file)
    y = to_categorical(data_dict['y'])
    x = data_dict['x']
    ids = data_dict['id']
    xterm = data_utils.pickle_load(val_conf.term_file)
    xfeat = data_utils.pickle_load(val_conf.feat_file)
    xfeat = scaler.transform(xfeat)
    print('feat shape', xfeat.shape)



    data_dict100 = data_utils.pickle_load(val_conf100.char_file)
    x100 = data_dict100['x']
    xterm100 = data_utils.pickle_load(val_conf100.term_file)
    xe100 = [[i for i in range(100)] for _ in range(y.shape[0])]
    xe100 = np.array(xe100)
    xe_term100 = [[i for i in range(100)] for _ in range(y.shape[0])]
    xe_term100 = np.array(xe_term100)

    data_dict200 = data_utils.pickle_load(val_conf200.char_file)
    x200 = data_dict200['x']
    xterm200 = data_utils.pickle_load(val_conf200.term_file)
    xe200 = [[i for i in range(200)] for _ in range(y.shape[0])]
    xe200 = np.array(xe200)
    xe_term200 = [[i for i in range(200)] for _ in range(y.shape[0])]
    xe_term200 = np.array(xe_term200)

    ys = []
    print('define model')
    model = HybridDenseModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                            PE=True, name='hybriddensemodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model

    model = HybridDenseMAModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                            PE=True, name='hybriddensemodelma_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('dense model done.')

    model = HybridSEModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                            PE=True, name='hybridsemodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('se model done.')

    print('start len 100 model')
    model = HybridConvModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, MAX_LEN=100, MAX_LEN_TERM=100,NUM_FEAT=8,
                            PE=True, name='hybridconvmodel_n100.h5')
    model.load_weights()
    y = model.predict([x100, xe100, xterm100, xe_term100, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid conv model done.')

    model = HybridGatedDeepCNNModel(char_embed_matrix=char_embed_matrix,
                                    term_embed_matrix=term_embed_matrix, MAX_LEN=100, MAX_LEN_TERM=100,NUM_FEAT=8,
                                    PE=True, name='hybridgateddeepcnnmodel_n100.h5')
    model.load_weights()
    y = model.predict([x100, xe100, xterm100, xe_term100, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid gated deep cnn model done.')

    model = HybridRCNNModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, MAX_LEN=100, MAX_LEN_TERM=100,NUM_FEAT=8,
                            PE=True, name='hybridrcnnmodel_n100.h5')
    model.load_weights()
    y = model.predict([x100, xe100, xterm100, xe_term100, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid RCNN model done.')

    # print('start len 200 model')
    # model = HybridConvModel(char_embed_matrix=char_embed_matrix,
    #                         term_embed_matrix=term_embed_matrix, MAX_LEN=200, MAX_LEN_TERM=200,NUM_FEAT=8,
    #                         PE=True, name='hybridconvmodel_n200.h5')
    # model.load_weights()
    # y = model.predict([x200, xe200, xterm200, xe_term200, xfeat, xtopic])
    # ys.append(y)
    # del model
    # print('hybrid conv model done.')
    #
    # model = HybridDPCNNModel(char_embed_matrix=char_embed_matrix,
    #                          term_embed_matrix=term_embed_matrix, MAX_LEN=200, MAX_LEN_TERM=200,NUM_FEAT=8,
    #                          PE=True, name='hybriddpcnnmodel_n200.h5')
    # model.load_weights()
    # y = model.predict([x200, xe200, xterm200, xe_term200, xfeat, xtopic])
    # ys.append(y)
    # del model
    # print('hybrid dpcnn model done.')
    #
    # model = HybridGatedDeepCNNModel(char_embed_matrix=char_embed_matrix,
    #                                 term_embed_matrix=term_embed_matrix, MAX_LEN=200, MAX_LEN_TERM=200,NUM_FEAT=8,
    #                                 PE=True, name='hybridgateddeepcnnmodel_n200.h5')
    # model.load_weights()
    # y = model.predict([x200, xe200, xterm200, xe_term200, xfeat, xtopic])
    # ys.append(y)
    # del model
    # print('hybrid gated deep cnn model done.')
    #
    # model = HybridRCNNModel(char_embed_matrix=char_embed_matrix,
    #                         term_embed_matrix=term_embed_matrix, MAX_LEN=200, MAX_LEN_TERM=200,NUM_FEAT=8,
    #                         PE=True, name='hybridrcnnmodel_n200.h5')
    # model.load_weights()
    # y = model.predict([x200, xe200, xterm200, xe_term200, xfeat, xtopic])
    # ys.append(y)
    # del model

    #这个模型太慢
    # model = ConditionAttModel(char_embed_matrix=char_embed_matrix,
    #                           term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
    #                           name='conditionattmodel_PE.h5', lr=0.001)
    # model.load_weights()
    # y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    # ys.append(y)
    # print('condition att model done.')

    model = ConditionConvModel(char_embed_matrix=char_embed_matrix,
                              term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
                              name='conditionconvmodel_PE.h5', lr=0.001)
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('condition conv model done.')

    model = ConditionDPCNNModel(char_embed_matrix=char_embed_matrix,
                               term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
                               name='conditiondpcnnmodel_PE.h5', lr=0.001)
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('condition dpcnn model done.')

    model = ConditionGatedConvModel(char_embed_matrix=char_embed_matrix,
                                term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
                                name='conditiongatedconvmodel_PE.h5', lr=0.001)
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('condition gated conv model done.')

    model = ConditionGatedDeepCNNModel(char_embed_matrix=char_embed_matrix,
                                    term_embed_matrix=term_embed_matrix, NUM_FEAT=8, PE=True,
                                    name='conditiongateddeepcnnmodel_PE.h5', lr=0.001)
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('condition gated deepcnn model done.')

    model = HybridAttModel(char_embed_matrix=char_embed_matrix,
                                      term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                                      PE=True, name = 'hybridattmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    print('hybrid att model done.')

    model = HybridConvModel(char_embed_matrix=char_embed_matrix,
                           term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                           PE=True, name='hybridconvmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid conv model done.')

    model = HybridDPCNNModel(char_embed_matrix=char_embed_matrix,
                            term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                            PE=True, name='hybriddpcnnmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid dpcnn model done.')

    model = HybridGatedDeepCNNModel(char_embed_matrix=char_embed_matrix,
                             term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                             PE=True, name='hybridgateddeepcnnmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid gated deep cnn model done.')

    model = HybridRCNNModel(char_embed_matrix=char_embed_matrix,
                                    term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                                    PE=True, name='hybridrcnnmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    del model
    print('hybrid rcnn model done.')

    model = HybridGatedConvTopicModel(char_embed_matrix=char_embed_matrix,
                                      term_embed_matrix=term_embed_matrix, NUM_FEAT=8,
                                      PE=True, name='hybridgatedconvtopicmodel_PE.h5')
    model.load_weights()
    y = model.predict([x, xe, xterm, xe_term, xfeat, xtopic])
    ys.append(y)
    print('hybrid gated conv topic done.')

    y = fasttextmodel.predict_char()
    ys.append(y)

    y = fasttextmodel.predict_term()
    ys.append(y)
    print(y.shape)
    print('fast text done.')

    #hybrid model
    model = HybridModel(char_embed_matrix=char_embed_matrix, term_embed_matrix=term_embed_matrix, NUM_FEAT=8)# + 37
    model.load_weights()
    y = model.predict([x, xterm, xfeat])
    ys.append( y )
    print(y.shape)
    print('hybrid model done.')
    ys = np.array(ys)
    print(ys.shape)
    return ys

def convert_onehot(y):
    """
    将one-hot表示转化为label index的格式
    :param y:
    :return:
    """
    yc = [np.argmax(yi) for yi in y]
    C = y.shape[1]
    ys = [[1.0 if i == yi else 0.0 for i in range(C)] for yi in yc]
    return np.array(ys)


def encode_main():
    lda_file='data/lda_vec_val.pkl'
    import data_utils100
    import data_utils200
    tn_conf = TrainConfigure()
    val_conf = ValidConfigure()
    val_conf200 = data_utils200.ValidConfigure()
    val_conf100 = data_utils100.ValidConfigure()
    ys_val = predict( tn_conf, lda_file, val_conf, val_conf100, val_conf200)

    import data_utils100
    import data_utils200
    tn_conf = TrainConfigure()
    val_conf = TrainConfigure()
    val_conf200 = data_utils200.TrainConfigure()
    val_conf100 = data_utils100.TrainConfigure()
    ys_train = predict(tn_conf, lda_file, val_conf, val_conf100, val_conf200)
    data_utils.pickle_dump((ys_train, ys_val), 'data/stack_y.pkl')


if __name__ == '__main__':
    SEED = 88
    np.random.seed(SEED)
    random.seed(SEED)
    encode_main( )
