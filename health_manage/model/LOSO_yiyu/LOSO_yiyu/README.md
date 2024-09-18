# LOSO实验：从20个人里面选取一个出来测试是否分类正确

## 实验结果：

选取一个人作为测试集，对样本投票：108个样本有50%即以上被分类正确则认为该受试者被分类正确。下图为例

![image-20240606231416560](https://gpt4-1317472746.cos.ap-shanghai.myqcloud.com/OpenAI/gpt/202406062314658.png)

## 实验环境：

- TensorFlow 2.7
- matplotlib 3.5
- NumPy 1.20
- scikit-learn 1.0
- SciPy 1.7

## ATCNet模型代码：

```python
def ATCNet_(n_classes, in_chans=22, in_samples=1125, n_windows=5, attention='mha',
            eegn_F1=16, eegn_D=2, eegn_kernelSize=64, eegn_poolSize=7, eegn_dropout=0.3,
            tcn_depth=2, tcn_kernelSize=4, tcn_filters=32, tcn_dropout=0.3,
            tcn_activation='elu', fuse='average'):
    input_1 = Input(shape=(1, in_chans, in_samples))  # TensorShape([None, 1, 22, 1125])
    # 维度变换 (None, 1125, 22, 1)
    input_2 = Permute((3, 2, 1))(input_1)

    # 权重衰减，卷积层的最大范数，是否使用logits
    dense_weightDecay = 0.5
    conv_weightDecay = 0.009
    conv_maxNorm = 0.6
    from_logits = False

    numFilters = eegn_F1
    F2 = numFilters * eegn_D

    # B.卷积（CV）块  (None, 1125, 22, 1) -> (None, Tc=20, 1, F2=32)
    block1 = Conv_block_(input_layer=input_2, F1=eegn_F1, D=eegn_D,
                         kernLength=eegn_kernelSize, poolSize=eegn_poolSize,
                         weightDecay=conv_weightDecay, maxNorm=conv_maxNorm,
                         in_chans=in_chans, dropout=eegn_dropout)
    # Lambda层压缩维度 (None, Tc=20, F2=32)
    block1 = Lambda(lambda x: x[:, :, -1, :])(block1)

    # C.基于卷积的滑动窗口（SW）   Sliding window
    sw_concat = []  # to store concatenated or averaged sliding window outputs
    for i in range(n_windows):  # n=5
        st = i  # 开始索引 = i
        end = block1.shape[1] - n_windows + i + 1  # 结束索引 = Tw + i = (Tc - n + 1) + i
        # 切片出当前滑动窗口的数据 Tc维度 Tw=20-5+1=16 (None, 16, 32)
        block2 = block1[:, st:end, :]

        # D.注意力（AT）块
        if attention is not None:
            if (attention == 'se' or attention == 'cbam'):
                block2 = Permute((2, 1))(block2)  # shape=(None, 32, 16)
                block2 = attention_block(block2, attention)
                block2 = Permute((2, 1))(block2)  # shape=(None, 16, 32)
            else:  # attention='mha'
                block2 = attention_block(block2, attention)  # (None, 16, 32)

        # E.时间卷积（TC）块 (None, 16, 32)
        block3 = TCN_block_(input_layer=block2, input_dimension=F2, depth=tcn_depth,
                            kernel_size=tcn_kernelSize, filters=tcn_filters,
                            weightDecay=conv_weightDecay, maxNorm=conv_maxNorm,
                            dropout=tcn_dropout, activation=tcn_activation)
        # 获取最后一个序列的特征图 (None, 32)
        block3 = Lambda(lambda x: x[:, -1, :])(block3)

        # Outputs of sliding window: Average_after_dense or concatenate_then_dense
        if (fuse == 'average'):  # fuse='average'
            # (None, 4)
            sw_concat.append(Dense(n_classes, kernel_regularizer=L2(dense_weightDecay))(block3))
        elif (fuse == 'concat'): ###1
            if i == 0:
                sw_concat = block3
            else:
                sw_concat = Concatenate()([sw_concat, block3])  # 将当前滑动窗口的表示与之前的表示进行拼接

    if (fuse == 'average'):
        if len(sw_concat) > 1:  # more than one window
            # list (None, 4) * n -> (None, 4)
            sw_concat = tf.keras.layers.Average()(sw_concat[:])
        else:  # one window (# windows = 1)
            sw_concat = sw_concat[0]
    elif (fuse == 'concat'):
        sw_concat = Dense(n_classes, kernel_regularizer=L2(dense_weightDecay))(sw_concat)

    if from_logits:  # No activation here because we are using from_logits=True
        out = Activation('linear', name='linear')(sw_concat)
    else:  # Using softmax activation
        out = Activation('softmax', name='softmax')(sw_concat)

    return Model(inputs=input_1, outputs=out)

def Conv_block_(input_layer, F1=4, kernLength=64, poolSize=8, D=2, in_chans=22,
                weightDecay=0.009, maxNorm=0.6, dropout=0.25):
    """ Conv_block
    
        Notes
        -----
        using  different regularization methods.
    """

    F2 = F1 * D
    # F1滤波器 (None, 1125, 22, 1) -> (None, 1125, 22, F1)
    block1 = Conv2D(F1, (kernLength, 1), padding='same', data_format='channels_last',
                    kernel_regularizer=L2(weightDecay),

                    # In a Conv2D layer with data_format="channels_last", the weight tensor has shape 
                    # (rows, cols, input_depth, output_depth), set axis to [0, 1, 2] to constrain 
                    # the weights of each filter tensor of size (rows, cols, input_depth).
                    kernel_constraint=max_norm(maxNorm, axis=[0, 1, 2]),
                    use_bias=False)(input_layer)
    # BN 批量归一化操作
    block1 = BatchNormalization(axis=-1)(block1)  # bn_axis = -1 if data_format() == 'channels_last' else 1

    # F2滤波器-深度可分离卷积 (None, 1125, 1, F2=F1*D=32)
    block2 = DepthwiseConv2D((1, in_chans),
                             depth_multiplier=D,
                             data_format='channels_last',
                             depthwise_regularizer=L2(weightDecay),
                             depthwise_constraint=max_norm(maxNorm, axis=[0, 1, 2]),
                             use_bias=False)(block1)
    block2 = BatchNormalization(axis=-1)(block2)
    block2 = Activation('elu')(block2)
    # 平均池化层 (None, 1125/8=140, 1, F2=32)
    block2 = AveragePooling2D((8, 1), data_format='channels_last')(block2)
    block2 = Dropout(dropout)(block2)

    # 空间卷积 (None, 140, 1, 32)
    block3 = Conv2D(F2, (16, 1),
                    data_format='channels_last',
                    kernel_regularizer=L2(weightDecay),
                    kernel_constraint=max_norm(maxNorm, axis=[0, 1, 2]),
                    use_bias=False, padding='same')(block2)
    block3 = BatchNormalization(axis=-1)(block3)
    block3 = Activation('elu')(block3)
    # 平均池化层 (None, 20, 1, 32)  poolSize=7
    block3 = AveragePooling2D((poolSize, 1), data_format='channels_last')(block3)
    block3 = Dropout(dropout)(block3)
    return block3

def TCN_block_(input_layer, input_dimension, depth, kernel_size, filters, dropout,
               weightDecay=0.009, maxNorm=0.6, activation='relu'):
    """ TCN_block from Bai et al 2018
        Temporal Convolutional Network (TCN)
        
        Notes
        -----
        using different regularization methods
    """
    # 一维（因果）卷积 (None, 16, 32) -> (None, 16, 32)
    block = Conv1D(filters, kernel_size=kernel_size, dilation_rate=1, activation='linear',
                   kernel_regularizer=L2(weightDecay),
                   kernel_constraint=max_norm(maxNorm, axis=[0, 1]),
                   padding='causal', kernel_initializer='he_uniform')(input_layer)
    block = BatchNormalization()(block)
    block = Activation(activation)(block)
    block = Dropout(dropout)(block)
    # 一维卷积
    block = Conv1D(filters, kernel_size=kernel_size, dilation_rate=1, activation='linear',
                   kernel_regularizer=L2(weightDecay),
                   kernel_constraint=max_norm(maxNorm, axis=[0, 1]),
                   padding='causal', kernel_initializer='he_uniform')(block)
    block = BatchNormalization()(block)
    block = Activation(activation)(block)
    block = Dropout(dropout)(block)

    # 残差连接
    if (input_dimension != filters):
        # 输入张量的维度和输出特征的维度不一致，则添加一个卷积层，将输入张量的维度调整为与输出特征相同
        conv = Conv1D(filters, kernel_size=1,
                      kernel_regularizer=L2(weightDecay),
                      kernel_constraint=max_norm(maxNorm, axis=[0, 1]),

                      padding='same')(input_layer)
        added = Add()([block, conv])
    else:
        added = Add()([block, input_layer])
    out = Activation(activation)(added)

    # 循环堆叠残差块
    for i in range(depth - 1): # depth=2
        # 卷积核的空洞率（dilation rate）会成指数增长 D=2
        # 增加模型的感受野，以捕捉输入序列的长程依赖关系
        block = Conv1D(filters, kernel_size=kernel_size, dilation_rate=2 ** (i + 1), activation='linear',
                       kernel_regularizer=L2(weightDecay),
                       kernel_constraint=max_norm(maxNorm, axis=[0, 1]),

                       padding='causal', kernel_initializer='he_uniform')(out)
        block = BatchNormalization()(block)
        block = Activation(activation)(block)
        block = Dropout(dropout)(block)
        # 一维卷积
        block = Conv1D(filters, kernel_size=kernel_size, dilation_rate=2 ** (i + 1), activation='linear',
                       kernel_regularizer=L2(weightDecay),
                       kernel_constraint=max_norm(maxNorm, axis=[0, 1]),

                       padding='causal', kernel_initializer='he_uniform')(block)
        block = BatchNormalization()(block)
        block = Activation(activation)(block)
        block = Dropout(dropout)(block)

        # 残差连接
        added = Add()([block, out])
        out = Activation(activation)(added)

    return out
```

## 数据处理，数据分割代码：

```python
def load_eeg_data_LOSO(data_path, subject,Leave_one, training):
    """
        加载 eegdata 数据集
          LOSO
    """
    # 每个人取的样本数
    # num_of_data = 118

    num_of_data = 108

    # 拼接control
    # 指定要遍历的文件夹路径
    folder_path = '/e/lb/dataset/eegdata/preprocessed clear data/Control/close' #原
    #folder_path = 'E:\Word\Documents\大三下\mne_data\机器学习数据\preprocessed clear data\Control\close'
    # 遍历文件夹内的所有文件
    control_list = []
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # 找到以set结尾的
            if file_name.endswith('.set'):
                file_path = os.path.join(root, file_name)
                raw = mne.io.read_epochs_eeglab(file_path)
                ctr_data = raw.get_data()
                # 取最后n条数据，修改数据条数n请到最上方改全局变量
                data = ctr_data[-(num_of_data)::, ::, ::]
                control_list.append(data)

    control_data = np.concatenate(control_list, axis=0)

    # 拼接exp first数据
    # 指定要遍历的文件夹路径
    # folder_path = '/e/lb/dataset/eegdata_cls/preprocessed clear data/EXP/first time/close eyes'  # first time
    folder_path = '/e/lb/dataset/eegdata_cls/preprocessed clear data/EXP/second time/closeyes-2'  # second time 原
    #folder_path = 'E:\Word\Documents\大三下\mne_data\机器学习数据\preprocessed clear data\EXP data_edf\EXP\second time\close eyes'  # second time


    # 遍历文件夹内的所有文件
    exp_f_list = []
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # 找到以edf结尾的
            if file_name.endswith('.edf'):
                file_path = os.path.join(root, file_name)
                raw = mne.io.read_raw_edf(file_path)
                raw.load_data()
                exp_data = raw.get_data()

                # 数据分段，代码参考之前发过的那个
                # 计算每个段的数据点数(500Hz *2秒)
                segment_length = int(500 * 2)
                # 获取数据的形状
                num_channels, num_samples = exp_data.shape
                # 分段数据
                segments = []
                for start in range(0, num_samples, segment_length):
                    end = start + segment_length
                    if end <= num_samples:
                        segment = exp_data[:, start:end]
                        segments.append(segment)
                # 将seqments转换为NumPy数组
                data_epochs = np.array(segments)

                # 取最后n条数据，修改数据条数n请到最上方改全局变量
                data = data_epochs[-(num_of_data)::, ::, ::]
                exp_f_list.append(data)

    exp_f_data = np.concatenate(exp_f_list, axis=0)

    # 拼接2部分样本
    all_data = np.concatenate((control_data, exp_f_data), axis=0)
    # 扩充维度以适应本模型
    # all_data = np.expand_dims(all_data, axis=1)

    # 手动创建label 这里由于该模型后续损失函数等原因，将标签设置为1，2而非0，1
    # train_control_lebel = np.ones(num_of_data * 10)
    # train_exp_lebel = np.full(num_of_data * 10, 2)
    train_control_lebel = np.zeros(num_of_data * 10)
    # train_control_lebel=train_control_lebel+2
    train_exp_lebel = np.ones(num_of_data * 10)

    all_label = np.concatenate((train_control_lebel, train_exp_lebel))

    # ---------------------------------------------------------------------------------#
    # 固定20个人选取1个人测试
    n = 1
    test_data = all_data[num_of_data * n * (Leave_one - 1):num_of_data * n * Leave_one:, ::, ::]
    test_label = all_label[num_of_data * n * (Leave_one-1):num_of_data * n * Leave_one:]

    train_data1 = all_data[0:num_of_data * n * (Leave_one-1):, ::, ::]
    train_data2 = all_data[num_of_data * n * (Leave_one):num_of_data * n * 20:, ::, ::]
    train_data = np.concatenate((train_data1, train_data2), axis=0)

    train_label1 = all_label[0:num_of_data * n * (Leave_one-1):]
    train_label2 = all_label[num_of_data * n * (Leave_one):num_of_data * n * 20:]
    train_label = np.concatenate((train_label1, train_label2), axis=0)
    # ---------------------------------------------------------------------------------#

    return train_data, train_label, test_data, test_label

```

## 可执行代码

运行压缩包内`main_TrainValTest.py`文件即可

实验数据参考 dataset 文件夹