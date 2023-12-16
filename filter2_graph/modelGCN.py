import dgl
from dgl.nn import GraphConv
import torch
import torch.nn as nn
import torch.nn.functional as F

import time
import numpy as np
import pandas as pd

# class and label
classes = ['主题壁纸', '体育赛事', '育儿', '便民服务-生活服务-生活类工具-租房招聘', '外卖购物', 
           '美食菜谱', '记事记账', '天气', '出行打车-地铁公交-定位导航-购票旅行', '医疗',
           '运动健康', '借贷', '金融服务', '社交', '视频直播',
           '音乐-音频编辑工具', '设计绘画-照片相机', '漫画', '阅读', '报刊新闻', 
           '学习-外语学习', '游戏-棋牌', '文档类工具-输入法', '办公类工具', '设备管理工具-网络类工具-浏览器-软件开发工具']
class2label = { '主题壁纸': 0,
                '体育赛事': 1,
                '育儿': 2,
                '便民服务': 3, '生活服务': 3, '生活类工具': 3, '租房招聘': 3,
                '外卖购物': 4,
                '美食菜谱': 5,
                '记事记账': 6,
                '天气': 7,
                '出行打车': 8, '地铁公交': 8, '定位导航': 8, '购票旅行': 8,
                '医疗': 9,
                '运动健康': 10,
                '借贷': 11,
                '金融服务': 12,
                '社交': 13,
                '视频直播': 14,
                '音乐': 15, '音频编辑工具': 15,
                '设计绘画': 16, '照片相机': 16, 
                '漫画': 17,
                '阅读': 18,
                '报刊新闻': 19,
                '学习': 20, '外语学习': 20, 
                '游戏': 21, '棋牌': 21,
                '文档类工具': 22, '输入法': 22,
                '办公类工具': 23,
                '设备管理工具': 24, '网络类工具': 24, '浏览器': 24, '软件开发工具': 24,
                }

# hyperparameterization
lr = 0.01
epochs = 500
h1_feats = 256
h2_feats = 128
n_classes = len(classes)
dropout = 0.5

# --------------- model part ---------------
class GCN(nn.Module):
    def __init__(self, in_feats, h1_feats, h2_feats, num_classes, dropout):
        super(GCN, self).__init__()
        self.conv1 = GraphConv(in_feats, h1_feats)
        self.conv2 = GraphConv(h1_feats, h2_feats)
        self.dropout = nn.Dropout(p=dropout)
        self.fc = nn.Linear(h2_feats, num_classes)
        self.fc.reset_parameters()

    def forward(self, g, in_feat):
        h = self.conv1(g, in_feat)
        h = F.relu(h)
        h = self.conv2(g, h)
        h = self.fc(h)
        h = torch.log_softmax(h, dim=-1)
        return h
  
# --------------- data part ---------------
# func: extracting [valid] edges from edge dictionary files
def get_graph(app2node_path, src2dst_path):
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Get Graph')
    app2node = np.load(app2node_path, allow_pickle='TRUE').item()
    edges = np.load(src2dst_path, allow_pickle='TRUE').item()
    edge_srcs = []
    edge_dsts = []
    for src in edges:
        for dst in edges[src]:
            edge_srcs.append(app2node[src])
            edge_dsts.append(app2node[dst])
            # bidirectional join to construct an undirected graph
            edge_srcs.append(app2node[dst])
            edge_dsts.append(app2node[src])
    # get graph
    u = torch.tensor(edge_srcs)
    v = torch.tensor(edge_dsts)
    g = dgl.DGLGraph((u,v))
    return g

# func: extract features from comm file, random initialization nodes without comm, uniform order by node id
# themes_comm_path: comment functionalities words; W2VModel_path: Word2vecmodel
def get_features(themes_comm_path, W2VModel_path, app2node_path):
    from gensim.models import word2vec
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Get Features')
    # load data
    print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Load Data', end=' ')
    data = pd.read_csv(themes_comm_path)
    data['themes'] = data.apply(lambda row: [s for s in row['themes'][1:-1].replace('\'','').split(', ') if not s == ''], axis=1)
    print(str(len(data)))
    # vectorization
    print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Get Vec')
    w2v = word2vec.Word2Vec.load(W2VModel_path)
    def get_random_features():
        return [1/64]*64
    def get_vecs_w2v(words):
        if type(words)==str:
            try:
                return w2v.wv[words]
            except Exception as e:
                return get_random_features()
        vec = [0]*64
        length = 0
        for word in words:
            try:
                word_vec = w2v.wv[word]
                for i in range(64):
                    vec[i] += word_vec[i]
                length += 1
            except Exception as e:
                continue           
        if length > 0:
            vec = [vec[i]/length for i in range(64)]
            return vec
        else:
            return get_random_features()
    data['vecs_comm'] = data.apply(lambda row: get_vecs_w2v(row['themes']), axis=1)
    # Add no comment data
    print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Add Node without Comm', end=' ')
    app2node = np.load(app2node_path, allow_pickle='TRUE').item()
    appids_nocomm = set(int(appid) for appid in app2node.keys())-set(data['appid'].to_list())
    for appid in appids_nocomm:
        data = data.append(pd.DataFrame([[appid, [], get_random_features()]], columns=data.columns))
    print(str(len(data)))
    # Sort by node id and delete the ones that are not in the figure
    print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Remove not Node', end=' ')
    data['node'] = data.apply(lambda row: app2node[str(row['appid'])] if str(row['appid']) in app2node else -1, axis=1)
    data = data.drop(data[data['node'] == -1].index)
    data.sort_values(by=['node'], axis=0, ascending=[True], inplace=True)
    print(str(len(data)))
    # return tensor
    return torch.tensor(data['vecs_comm'].to_list()).float()

# func: extract the labels from the classed profile file
# class_profile_path: class file from modelRFC, fake_appids: appid set of Mask Apps
def get_labels(class_profile_path, fake_appids, app2node_path):
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Get Labels', end=' ')
    # load data
    data = pd.read_csv(class_profile_path)[['appid','pred_class']]
    # modify the label of the Mask Apps
    data['label'] = data.apply(lambda row: class2label['视频直播'] if str(row['appid']) in fake_appids else class2label[row['pred_class']], axis=1)
    # sort by node id
    app2node = np.load(app2node_path, allow_pickle='TRUE').item()
    data['node'] = data.apply(lambda row: app2node[str(row['appid'])] if str(row['appid']) in app2node else -1, axis=1)
    data= data.drop(data[data['node'] == -1].index)
    data.sort_values(by=['node'], axis=0, ascending=[True], inplace=True)
    print(str(len(data)))
    # return tensor
    return torch.tensor(data['label'].to_list())

# divide the data set
def get_mask(len_, n):
    train_mask = [True]*len_
    val_mask = [False]*len_
    for i in range(len_):
        if i%10 == n:
            train_mask[i] = False
            val_mask[i] = True
    return torch.tensor(train_mask), torch.tensor(val_mask)

# --------------- train part ---------------
# func: evaluate
def evaluate(gcn, graph, features, labels, nid=None):
    gcn.eval()
    with torch.no_grad():
        logits = gcn(graph, features)
        if not nid == None:
            logits = logits[nid]
            labels = labels[nid]
        _, indices = torch.max(logits, dim=1)
        correct = torch.sum(indices == labels)
        return correct.item() * 1.0 / len(labels)

# func: train
def train(g, gcn, features, labels, train_mask, val_mask, lr, epochs, gcn_path):
    gcn_optimizer = torch.optim.Adam(gcn.parameters(), lr=lr, weight_decay=0.0001)
    max_acc = 0
    for e in range(epochs):
        # Forward
        preds = gcn(g, features)
        # Compute loss
        loss = F.cross_entropy(preds[train_mask], labels[train_mask])
        # Backward
        gcn_optimizer.zero_grad()
        loss.backward()
        gcn_optimizer.step()
        # evaluate
        if not e%10 or e==epochs-1:
            # train acc
            train_nid = train_mask.nonzero().squeeze()
            train_acc = evaluate(gcn, g, features, labels, train_nid)
            # val acc
            val_nid = val_mask.nonzero().squeeze()
            val_acc = evaluate(gcn, g, features, labels, val_nid)
            print("\tEpoch {:03d}  | Loss {:.4f} | Train Accuracy {:.4f} | Val Accuracy {:.4f} |".format(e, loss.item(), train_acc, val_acc))
            # save
            if val_acc > max_acc:
                max_acc = val_acc
                torch.save(gcn.state_dict(), gcn_path)
    return max_acc
def train_10(g, features, labels, n_classes, lr, epochs, h1_feats, h2_feats, dropout, gcn_path):
    avg_acc = 0
    for i in range(10):
        print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+" ----- Round "+str(i))
        gcn = GCN(in_feats=features.shape[1], h1_feats=h1_feats, h2_feats=h2_feats, num_classes=n_classes, dropout=dropout)
        train_mask, val_mask = get_mask(features.shape[0], i)
        acc = train(g, gcn, features, labels, train_mask, val_mask, lr, epochs, gcn_path)
        avg_acc = avg_acc + acc
    print("\tVal Avg Accuracy {:.4f}".format(avg_acc/10)) 
    acc = evaluate(gcn, g, features, labels)
    print("\tAll Data Accuracy {:.4f}".format(acc)) 
    return round(avg_acc/10, 4), round(acc, 4)

# main
def main(gcn_path):
    g = get_graph()
    features = get_features()
    # torch.save(features, features_path)
    # features = torch.load(features_path)
    labels = get_labels()
    train_10(g, features, labels, n_classes, lr, epochs, h1_feats, h2_feats, dropout, gcn_path)
    
# --------------- using part ---------------
# get the comment category matrix
def getMatrix(class_profile_path, gcn_path, app2node_path, pred_graph_path, comm_matrix_path):
    # get nodes
    print('\t'+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+' ----- Get Suspicious Node')
    app2node = np.load(app2node_path, allow_pickle='TRUE').item()
    data = pd.read_csv(class_profile_path)[['appid']]
    data['node'] = data.apply(lambda row: app2node[str(row['appid'])] if str(row['appid']) in app2node else -1, axis=1)
    data= data.drop(data[data['node'] == -1].index)
    data.sort_values(by=['node'], axis=0, ascending=[True], inplace=True)
    # load graph
    g = get_graph()
    features = get_features()
    # torch.save(features, features_path)
    # features = torch.load(features_path)
    # load model
    gcn = GCN(in_feats=64, h1_feats=h1_feats, h2_feats=h2_feats, num_classes=n_classes, dropout=dropout)
    gcn.load_state_dict(torch.load(gcn_path))
    # predict
    logits = gcn(g, features)
    _, indices = torch.max(logits, dim=1)
    data['matrix'] = logits.detach().numpy().tolist()
    # save
    data['pred'] = [int(y) for y in indices]
    data['class_c'] = data.apply(lambda row: classes[row['pred']], axis=1)
    data[['class_c', 'appid', 'name','genre']].to_csv(pred_graph_path, index=False)
    # return matrix
    torch.save(data[['appid', 'matrix']], comm_matrix_path)
    return data[['appid', 'matrix']]
