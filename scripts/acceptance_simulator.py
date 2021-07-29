from math import log
ACCEPTANCE_MULTIPLIER = 0.5

print('Population | Required acceptance')
for i in range(1, 10):
    print(f'{str(i).rjust(10)} | {str(round(log(i)*ACCEPTANCE_MULTIPLIER)+1).rjust(1)}')
    # +1 because acceptance has to be > than threshold. +1 is just for simulation.
    # print(f'{str(i).rjust(10)} | {str(round(log(i)*ACCEPTANCE_MULTIPLIER)).rjust(1)}')

    # print(f' {str(i).rjust(9)} | {str(round(i*ACCEPTANCE_MULTIPLIER)+1).rjust(1)}')

