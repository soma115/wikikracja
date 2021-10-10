'''
New person is accepted when his/her Reputation is > (above) Required acceptance.
Existing person is expeled when his/her Reputation is < (below) Required acceptance.
This is > and < but not >= or <=. So Reputation has to be Required+1 or Required-1 to accept or ban user.

ACCEPTANCE_MULTIPLIER
Higher = harder to accept new person AND easier to ban existing person.
Lower = easier to accept new person AND harder to ban existing person.
'''
from math import log, floor, ceil
'''
max_possible_acceptance = n_users - 2
-2 is there because first 3 users needs to be accepted without explicit approval from others. First 3 users are usualy bulk-generated.
Sane range 1.6 - 2.7
'''
ACCEPTANCE_MULTIPLIER = 9
# ACCEPTANCE_MULTIPLIER = 7

print('Population | Required acceptance')
for i in range(0, 20):
    # result = round(log(i * ACCEPTANCE_MULTIPLIER))
    result = floor(log(i * ACCEPTANCE_MULTIPLIER + 1))-2
    # a = floor(i*ACCEPTANCE_MULTIPLIER)
    print(f'{str(i).rjust(10)} | {str(result).rjust(1)}')
    if i <= result:
        print('error')
