import torch
import torch.nn as nn
from tqdm.notebook import tqdm
from torch.utils.data import DataLoader
from sklearn.model_selection import KFold
from model.classifer_3 import BallDataset, seed_everything, Rnn
from model.dataProcess import process_data
import matplotlib.pyplot as plt
import time
import os

use_gpu = torch.cuda.is_available()  # 判断是否有GPU加速
if use_gpu:
    device = 'cuda'
else:
    device = 'cpu'
device = 'cpu'
gamma = 0.8
seed = 10
max_len = 512
batch_size = 512
seed_everything(seed)


def kfold_val(data_path, total_num, lr, epochs):
    with open('../result/status/status.txt', mode='w', encoding='utf-8') as f:
        save_folder = './../result/val_img/' + time.strftime("%Y_%m_%d_%H_%M", time.localtime())
        n_splits = 5
        data = process_data(data_path)
        X = data['X']
        y = data['y']
        X = X.reshape(-1, 1024, 1)
        avg_list = []
        for i in range(total_num):
            acc_list = []
            print('kfold:{}'.format(i))
            kf = KFold(n_splits=n_splits, shuffle=True)
            count = 1
            for train_index, test_index in kf.split(X):
                print('Iteration-->{}'.format(count))
                X_train, X_test = X[train_index], X[test_index]
                y_train, y_test = y[train_index], y[test_index]
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
                count += 1
            result = 0
            print(acc_list, acc_list.__len__())
            for item in acc_list:
                result += item
            avg = result / len(acc_list)
            avg_list.append(avg)
            plt.figure(figsize=(4, 3))
            x = range(epochs * n_splits)
            plt.plot(x, acc_list, label='val_accuracy')
            plt.title('Cross_val_accuracy')
            plt.ylim((0, 1))
            plt.legend()
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
                plt.savefig(save_folder + '/' + str(i) + '.jpg')
            else:
                plt.savefig(save_folder + '/' + str(i) + '.jpg')
            # plt.show()
        f.write(save_folder + '\n')
        sum = 0
        for ele in avg_list:
            sum += ele
        final_avg_acc = sum / len(avg_list)
        f.write(str(final_avg_acc) + '\n')
        f.write('end')
        f.close()

# torch.save(model.state_dict(), './result/cross_val/{}_{}_bestAcc.pt'.format(i, count))
