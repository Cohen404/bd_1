import numpy as np

acc_array = np.array([[89.35, 88.89, 79.17, 99.07, 87.96, 73.61, 51.85, 75.46, 71.30, 79.63],
                      [94.91, 82.87, 93.06, 86.11, 99.54, 98.15, 94.44, 92.13, 87.04, 87.96],
                      [56.48, 61.11, 52.78, 67.13, 71.76, 53.24],
                      ])
# l = np.arange(1,11).reshape(2,5)
# print(l[0:0])
# x=l[0:0,:]
#
# print(l)
#
# xl=np.concatenate((x,l),axis=0)
# num_of_data=108
# train_control_lebel1 = np.ones(num_of_data * 10)
# train_exp_lebel1 = np.full(num_of_data * 10, 2,dtype='float64')
# print(train_control_lebel1,train_exp_lebel1)
# train_control_lebel = np.zeros(num_of_data * 10)
# train_exp_lebel = np.ones(num_of_data * 10)
# train_control_lebel=train_control_lebel+2
# print(train_control_lebel,train_exp_lebel)
print(acc_array)

y_test = np.array([
    [2, 5, 1],
    [3, 6, 2],
    [8, 1, 0]
])
indices = y_test.argmax(axis=-2)