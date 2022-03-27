from LoadFile.Load import *

data = LoadFile("data.txt")

# print(data.nb_contacts)
# print(data.center_masse)
list_grasp_qualities = []
for grasp in data.list_grasps:
    list_grasp_qualities.append([grasp.calculate_Q_MVS(), grasp.calculate_Q_VEM(),
                                 grasp.calculate_Q_IIP(), grasp.calculate_Q_DCC()])

for grasp_qualities in list_grasp_qualities:
    print(grasp_qualities)

list_grasp_qualities = np.array(list_grasp_qualities)
for i in range(4):
    max_column_i = list_grasp_qualities[:, i].max()
    min_column_i = list_grasp_qualities[:, i].min()
    for j in range(len(list_grasp_qualities)):
        list_grasp_qualities[j][i] = (list_grasp_qualities[j][i] - min_column_i)/(max_column_i - min_column_i)
        if i == 3:
            list_grasp_qualities[j][i] = 1 - list_grasp_qualities[j][i]

for grasp_qualities in list_grasp_qualities:
    print(grasp_qualities)

list_score = []
max_score = 0
max_score_index = 0
for i in range(len(list_grasp_qualities)):
    list_score.append(sum(list_grasp_qualities[i]))
    if sum(list_grasp_qualities[i]) > max_score:
        max_score = sum(list_grasp_qualities[i])
        max_score_index = i

print(max_score, max_score_index)
