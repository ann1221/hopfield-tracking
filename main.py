import pandas as pd
import torch
from matplotlib import pyplot as plt
from torch import tensor, full

from generator import gen_many_events
from segment import energy

torch.set_default_tensor_type(torch.cuda.FloatTensor)

pos = next(gen_many_events(1, 10))
pos = [tensor(p) for p in pos]
E = energy(pos, alpha=0.0001, beta=.0003, curvature_cosine_power=5)
act = [full((len(a), len(b)), 0.1, requires_grad=True) for a, b in zip(pos, pos[1:])]
perfect_act = [torch.eye(len(a)) for a in act]

perfect_act = [torch.eye(len(a)) for a in act]

T = 50.

history = []

for i in range(100):
    e = E(act)
    history.append((e.item(), sum([act[i].mean().item() for i in range(7)]) / 7))
    e.backward()
    for j in range(len(act)):
        next_act = 0.5 * (1 + torch.tanh(- act[j].grad / T))
        act[j] = next_act.clone().detach().requires_grad_(True)
history = pd.DataFrame(history, columns=['e', 'a'])

history.e.plot()
plt.show()
history.a.plot()
plt.show()
history['positive'] = history.e - history.e.min()
history.positive.plot(logy=True)
plt.show()
for i in range(7):
    plt.imshow(act[i].cpu().detach().numpy(), vmin=0, vmax=1, cmap='gray')
    plt.show()

THRESHOLD = 0.5

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(1, 1, 1)

fig = plt.figure(figsize=(10, 10))

ax = fig.add_subplot(1, 1, 1, projection='3d')
ax.set_zlabel('Z')
ax.set_xlabel('X')
ax.set_ylabel('Y')
count = 0

for i in range(7):
    p1 = pos[i].cpu()
    p2 = pos[i + 1].cpu()
    a = act[i].cpu()
    a_good = perfect_act[i].cpu()
    print(i, '...')
    for j in range(len(p1)):
        for k in range(len(p2)):
            positive = a[j, k] > THRESHOLD
            true = a_good[j, k] > THRESHOLD
            if positive and true:
                color = 'black'
            elif positive and not true:
                color = 'red'
            elif not positive and true:
                color = 'blue'
            else:
                continue
            xs = [p1[j, 0], p2[k, 0]]
            ys = [p1[j, 1], p2[k, 1]]
            zs = [p1[j, 2], p2[k, 2]]
            ax.plot(xs, ys, zs,
                    color=color,
                    linewidth=1.,
                    marker='.')
plt.show()