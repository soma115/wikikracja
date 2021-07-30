from math import log
ACCEPTANCE_MULTIPLIER = 0.72  # Sane values: min:0.46 max:0.72
# Higher = harder to accept new person.
# Higher = easier to ban existing person.

print('Population | Required acceptance')
for i in range(1, 60):
    # +1 because acceptance has to be > than threshold. +1 is just for simulation.
    # print(f'{str(i).rjust(10)} | {str(round(log(i)*ACCEPTANCE_MULTIPLIER)+1).rjust(1)}')

    # bez +1
    print(f'{str(i).rjust(10)} | {str(round(log(i)*ACCEPTANCE_MULTIPLIER)).rjust(1)}')

