import os
import time
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from tqdm.notebook import tqdm
from torch.utils.data import DataLoader, Dataset
import numpy as np
import random
from model.dataProcess import process_data
from datetime import datetime

batch_size = 512
use_gpu = torch.cuda.is_available()  # 判断是否有GPU加速
if use_gpu:
    device = 'cuda'
else:
    device = 'cpu'
device = 'cpu'
# epochs = 1
lr = 0.002
gamma = 0.8
seed = 10
max_len = 512


def seed_everything(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True


seed_everything(seed)


# device = 'cuda'


class BallDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class Rnn(nn.Module):
    def __init__(self, in_dim, hidden_dim, n_layer, n_class):
        super(Rnn, self).__init__()
        self.n_layer = n_layer
        self.hidden_dim = hidden_dim
        self.lstm = nn.LSTM(in_dim, hidden_dim, n_layer,
                            batch_first=True)
        self.activation = nn.ReLU()
        self.conv1 = nn.Conv1d(1, hidden_dim // 4, kernel_size=3, padding='same')
        self.pool1 = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(hidden_dim // 4, hidden_dim // 8, kernel_size=3, padding='same')
        self.pool2 = nn.MaxPool1d(2)
        self.conv3 = nn.Conv1d(hidden_dim // 8, hidden_dim // 16, kernel_size=3, padding='same')
        self.pool3 = nn.MaxPool1d(2)
        self.cnn_linear = nn.Linear(hidden_dim // 16 * 1024 // 8, hidden_dim // 16)

        self.linear = nn.Linear(hidden_dim + hidden_dim // 16, hidden_dim // 2)
        self.classifier = nn.Linear(hidden_dim // 2, n_class)

        self.norm1 = nn.BatchNorm1d(hidden_dim // 4)
        self.norm2 = nn.BatchNorm1d(hidden_dim // 8)
        self.norm3 = nn.BatchNorm1d(hidden_dim // 16)
        self.m = nn.Dropout(p=0.1)

    def forward(self, x):
        shape = x.shape
        x = x.permute(0, 2, 1)
        out, _ = self.lstm(x)
        out = out[:, -1, :]

        # CNN
        cout = x.transpose(2, 1)
        cout = cout.permute(0, 2, 1)
        cout = self.activation(self.norm1(self.conv1(cout)))
        cout = self.pool1(cout)

        cout = self.activation(self.norm2(self.conv2(cout)))
        cout = self.pool2(cout)

        cout = self.activation(self.norm3(self.conv3(cout)))
        cout = self.pool3(cout)

        cout = cout.reshape(x.shape[0], -1)
        cout = self.activation(self.cnn_linear(cout))

        out = torch.cat([out, cout], 1)
        out = self.linear(out)
        out = self.classifier(out)
        return out


def train(data_path, epochs):
    with open('../result/status/status.txt', mode='w', encoding='utf-8') as f:
        f.write(str(datetime.now().replace(microsecond=0, second=0)) + '\n')
        data = process_data(data_path)
        X = data['X']
        y = data['y']
        X = X.reshape(-1, 1024, 1)
        acc_list = []
        X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                            test_size=0.2,
                                                            random_state=10)
        train_data = BallDataset(X_train, y_train)
        valid_data = BallDataset(X_test, y_test)

        train_loader = DataLoader(dataset=train_data, batch_size=batch_size, shuffle=True)
        valid_loader = DataLoader(dataset=valid_data, batch_size=batch_size, shuffle=True)

        model = Rnn(1024, 128, 2, 3).to(device)
        criterion = nn.CrossEntropyLoss().to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=gamma)

        torch.no_grad()
        for epoch in range(epochs):
            epoch_loss = 0
            epoch_accuracy = 0

            for data, label in tqdm(train_loader):
                data = data.float().to(device)
                label = label.to(device)

                output = model(data)
                loss = criterion(output, label.to(torch.int64))

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                acc = (output.argmax(dim=1) == label).float().mean()
                epoch_accuracy += acc / len(train_loader)
                epoch_loss += loss / len(train_loader)

            with torch.no_grad():
                epoch_val_accuracy = 0
                epoch_val_loss = 0
                for data, label in valid_loader:
                    data = data.float().to(device)
                    label = label.to(device)

                    val_output = model(data)
                    val_loss = criterion(val_output, label.to(torch.int64))
                    acc = (val_output.argmax(dim=1) == label).float().mean()
                    epoch_val_accuracy += acc / len(valid_loader)
                    epoch_val_loss += val_loss / len(valid_loader)
                acc_list.append(epoch_val_accuracy.cpu().numpy())
            print(
                f"Epoch : {epoch + 1} - loss : {epoch_loss:.4f} - acc: {epoch_accuracy:.4f} - val_loss : {epoch_val_loss:.4f} - val_acc: {epoch_val_accuracy:.4f}\n"
            )
        f.write(str(datetime.now().replace(microsecond=0, second=0)) + '\n')
        count = 0
        for item in acc_list:
            count += item
        model_path = './../result/model/cnn_' + time.strftime("%Y_%m_%d_%H_%M", time.localtime()) + '.pt'
        torch.save(model, model_path)
        f.write(model_path + '\n')
        f.write('end')
        f.close()


def modelTest(data_path, model_path):
    with open('../result/status/status.txt', mode='w', encoding='utf-8') as f:
        f.write(str(datetime.now().replace(microsecond=0, second=0)) + '\n')
        data = process_data(data_path)
        X = data['X']
        y = data['y']
        X = X.reshape(-1, 1024, 1)
        acc_list = []
        test_data = BallDataset(X, y)
        test_loader = DataLoader(dataset=test_data, batch_size=batch_size, shuffle=True)
        # model = torch.load(model_path)
        model = torch.load(model_path, map_location='cpu')
        model.eval()
        torch.no_grad()
        for epoch in range(10):
            epoch_accuracy = 0
            for data, label in tqdm(test_loader):
                data = data.float().to(device)
                label = label.to(device)
                output = model(data)
                acc = (output.argmax(dim=1) == label).float().mean()
                epoch_accuracy += acc / len(test_loader)
            acc_list.append(epoch_accuracy.cpu().numpy())
            print(
                f"acc: {epoch_accuracy:.4f} \n"
            )
        count = 0
        f.write(str(datetime.now().replace(microsecond=0, second=0)) + '\n')
        for item in acc_list:
            count += item
        avg_acc = count / len(acc_list)
        f.write(str(avg_acc) + '\n')
        f.write('end')
        f.close()
        # result_list.append(avg_acc)
        # return result_list
