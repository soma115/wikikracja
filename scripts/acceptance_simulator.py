'''
New person is accepted when his/her Reputation is > (above) Required acceptance.
Existing person is expeled when his/her Reputation is < (below) Required acceptance.
This is > and < but not >= or <=. So Reputation has to be Required+1 or Required-1 to accept or ban user.

ACCEPTANCE_MULTIPLIER
Higher = harder to accept new person AND easier to ban existing person.
Lower = easier to accept new person AND harder to ban existing person.
'''

from math import log
ACCEPTANCE_MULTIPLIER = 2.164  # Sane values: min:0.46 max:2.164042561333445080506976

print('Population | Required acceptance')
for i in range(1, 20):
    print(f'{str(i).rjust(10)} | {str(round(log(i)*ACCEPTANCE_MULTIPLIER)).rjust(1)}')
