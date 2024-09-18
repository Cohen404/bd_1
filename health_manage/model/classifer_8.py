from model.parse_data import process_data1, process_data, process_data4

import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from tqdm.notebook import tqdm
from torch.utils.data import DataLoader, Dataset
import numpy as np
import random
from sklearn import metrics
import os
import pickle as pkl
import time

class BasicConvResBlock(nn.Module):

    def __init__(self, input_dim=128, n_filters=256, kernel_size=3, padding=1, stride=1, shortcut=True, h =0.1, downsample=None):
        super(BasicConvResBlock, self).__init__()

        self.downsample = downsample
        self.shortcut = shortcut
        self.h = h
        self.m=nn.Dropout(p=0.1)
        self.conv1 = nn.Conv1d(input_dim, n_filters, kernel_size=kernel_size, padding=padding, stride=stride)
        self.bn1 = nn.BatchNorm1d(n_filters)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv1d(n_filters, n_filters, kernel_size=kernel_size, padding=padding, stride=stride)
        self.bn2 = nn.BatchNorm1d(n_filters)

    def forward(self, x):

        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.shortcut:
            if self.downsample is not None:
                residual = self.downsample(x)
            out = self.h * out + residual
        #out=self.m(out)
        out = self.relu(out)

        return out

class CNN(nn.Module):
    def __init__(self,input_channel,dropout,hidden_dim,n_class, shortcut=True, h = 0.1):
        super(CNN,self).__init__()
        self.transformer_maxpool=nn.MaxPool1d(2)
        layers = []
        n_conv_block_64, n_conv_block_128, n_conv_block_256, n_conv_block_512 = 1, 1, 1, 1
        layers.append(BasicConvResBlock(input_dim=4, n_filters=4, kernel_size=3, padding=1, shortcut=shortcut, h=h))
        for _ in range(n_conv_block_64 - 1):
            layers.append(
                BasicConvResBlock(input_dim=input_channel, n_filters=input_channel, kernel_size=3, padding=1, shortcut=shortcut, h=h))
        layers.append(nn.MaxPool1d(kernel_size=3, stride=2, padding=1))  # l = initial length / 2

        ds = nn.Sequential(nn.Conv1d(input_channel, 128, kernel_size=1, stride=1, bias=False), nn.BatchNorm1d(128))
        layers.append(BasicConvResBlock(input_dim=4, n_filters=128, kernel_size=3, padding=1, shortcut=shortcut, h=h,
                                        downsample=ds))
        for _ in range(n_conv_block_128 - 1):
            layers.append(
                BasicConvResBlock(input_dim=128, n_filters=128, kernel_size=3, padding=1, shortcut=shortcut, h=h))
        layers.append(nn.MaxPool1d(kernel_size=3, stride=2, padding=1))  # l = initial length / 4

        ds = nn.Sequential(nn.Conv1d(128, 256, kernel_size=1, stride=1, bias=False), nn.BatchNorm1d(256))
        layers.append(BasicConvResBlock(input_dim=128, n_filters=256, kernel_size=3, padding=1, shortcut=shortcut, h=h,
                                        downsample=ds))
        for _ in range(n_conv_block_256 - 1):
            layers.append(
                BasicConvResBlock(input_dim=32, n_filters=32, kernel_size=3, padding=1, shortcut=shortcut, h=h))
        layers.append(nn.MaxPool1d(kernel_size=3, stride=2, padding=1))

        ds = nn.Sequential(nn.Conv1d(256, 32, kernel_size=1, stride=1, bias=False), nn.BatchNorm1d(32))
        layers.append(BasicConvResBlock(input_dim=256, n_filters=32, kernel_size=3, padding=1, shortcut=shortcut, h=h,
                                        downsample=ds))
        for _ in range(n_conv_block_512 - 1):
            layers.append(
                BasicConvResBlock(input_dim=32, n_filters=32, kernel_size=3, padding=1, shortcut=shortcut, h=h))

        layers.append(nn.AdaptiveMaxPool1d(8))
        self.m = nn.Dropout(p=dropout)

        #self.linear = nn.Linear(128*2, hidden_dim * 2)
        self.classifier = nn.Linear(hidden_dim * 2, n_class)
        self.layers = nn.Sequential(*layers)

    def att_cnn(self, x, fc1, fc2):
        flat = torch.mean(x, dim=2)

        attn_weights = F.relu(fc1(flat))
        attn_weights = F.softmax(fc2(attn_weights))

        shape = attn_weights.shape
        attn_weights = attn_weights.view(shape[0], shape[1], 1)

        attn_out = x * attn_weights
        return attn_out

    def forward(self, x):

        x= x.transpose(2, 1)
        block_out=self.layers(x)

        block_out=torch.flatten(block_out,start_dim=1)
        #last_out=self.linear(block_out)
        last_out=self.m(block_out)
        last_out= self.classifier(last_out)
        return last_out


class BallDataset(Dataset):
    def __init__(self, X):
        self.X = X

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx]

#
# def seed_everything(seed):
#     random.seed(seed)
#     os.environ['PYTHONHASHSEED'] = str(seed)
#     np.random.seed(seed)
#     torch.manual_seed(seed)
#     torch.cuda.manual_seed(seed)
#     torch.cuda.manual_seed_all(seed)
#     torch.backends.cudnn.deterministic = True
#
#
# with open('data/4_1024_data_1800_8.pkl','rb') as f:
#     data = pkl.load(f)
# X = data['X']
# y = data['y']
# new=np.swapaxes(X, 1, 2)
# X=new.reshape(-1,1024,4)
# y=y.reshape(-1)
#
#
# X_train,X_test, y_train, y_test = train_test_split(X,y,
#                                           test_size=0.2,
#                                           random_state=1)
#
#
# train_data = BallDataset(X_train,y_train)
# valid_data = BallDataset(X_test,y_test)
#
# batch_size=10
# num_class=8
use_gpu = torch.cuda.is_available()  # ?????GPU??
if use_gpu:
    device = 'cuda'
else:
    device = 'cpu'
device = 'cpu'
# epochs = 100
# lr = 0.001
# gamma = 0.8
# seed = 10
#
# train_loader = DataLoader(dataset = train_data, batch_size=batch_size, shuffle=True )
# valid_loader = DataLoader(dataset = valid_data, batch_size=batch_size, shuffle=True)
#
#
#
# model = CNN(input_channel=4,dropout=0.3,hidden_dim=128,n_class=num_class).to(device)  # ?????28x28#self,input_dim,num_head,feed_dim,dropout,hidden_dim,n_class
# #model=Rnn(1, 128, 2, num_class,1024).to(device)
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model.parameters(),lr=lr)
# scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=gamma)
# tr_accs = []
# tr_loss = []
# te_accs = []
# te_loss = []
# te_recall=[]
# te_f1=[]
# for epoch in range(epochs):
#     epoch_loss = 0
#     epoch_accuracy = 0
#
#     for data, label in tqdm(train_loader):
#         data = data.float().to(device)
#         label = label.to(device)
#
#         output = model(data)
# #         print(output.shape)
#         loss = criterion(output, label)
#
#         optimizer.zero_grad()
#         loss.backward()
#         optimizer.step()
#
#         acc = (output.argmax(dim=1) == label).float().mean()
#         epoch_accuracy += acc / len(train_loader)
#         epoch_loss += loss / len(train_loader)
#
#     with torch.no_grad():
#         epoch_val_accuracy = 0
#         epoch_val_loss = 0
#         for data, label in valid_loader:
#             data = data.float().to(device)
#             label = label.to(device)
#
#             val_output = model(data)
#             val_loss = criterion(val_output, label)
#
#             acc = (val_output.argmax(dim=1) == label).float().mean()
#             epoch_val_accuracy += acc / len(valid_loader)
#             epoch_val_loss += val_loss / len(valid_loader)
#
#     print(
#         f"Epoch : {epoch+1} - loss : {epoch_loss:.4f} - acc: {epoch_accuracy:.4f} - val_loss : {epoch_val_loss:.4f} - val_acc: {epoch_val_accuracy:.4f}\n"
#     )
#     tr_accs.append(epoch_accuracy.cpu())
#     tr_loss.append(epoch_loss.cpu())
#     te_accs.append(epoch_val_accuracy.cpu())
#     te_loss.append(epoch_val_loss.cpu())
#
# torch.save(model,'8_classes_1024_h_0.1.pt')

# batch_size = 960
def get_zs(l):
    res = {}
    l.sort()
    for i in l:
        if i >= 0:
            res[i] = l.count(i)
    for k, v in res.items():
        if v == max(res.values()):
            return k


def modelTest_RUL(data_path, model_path):
    data = process_data4(data_path)#960，1024，4

    test_data = BallDataset(data)
    test_loader = DataLoader(dataset=test_data, batch_size=960, shuffle=True)

    # model = torch.load(model_path)
    model = torch.load(model_path,map_location='cpu')
    model.eval()
    torch.no_grad()
    for data in tqdm(test_loader):
        data = data.float().to(device)
        # print(data.shape)
        output = model(data)

        # print(output.shape)
        # print(output.argmax(dim=1))
        # print(output.argmax(dim=1).shape)

    result = output.argmax(dim=1)
    result = result.cpu().numpy().tolist()
    # 求众数
    type = get_zs(result)   # 类别为0，1，2，3，4，5，6，7
    # 根据类别获取剩余寿命，进入声学故障之后寿命为2895小时
    every_time = 2895/8
    rul = int(2895-(type+1)*every_time)
    # print("剩余寿命>=", rul)
    return rul


if __name__ == '__main__':
    model_path = 'D:\\Program Files\\PycharmProject\\Health_Manage\\model\\8_classes_1024_h_0.1.pt'
    data_path = 'D:\\Program Files\\PycharmProject\\Health_Manage\\data\\32_1800_0.mat'
    lii = modelTest_RUL(data_path, model_path)
    print("结果")
    print(lii)
