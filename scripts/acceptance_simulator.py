from math import log
ACCEPTANCE_MULTIPLIER = 1.6
for i in range(1, 30):
    print(f'Population: {i}; Required acceptance: {round(log(i)*ACCEPTANCE_MULTIPLIER)}; Half: {round(i/2)};')