# Amortized Loan Simulator
import pandas as pd

def calculate_interest(P,r):
    '''Calculate simple monthly interest payment
    '''
    
    return P*r/12
    
def calculate_snapshot_monthly(P, r, n):
    '''Calculate amortized monthly payment
    
    P (int): initial principal
    r (float): interest per period (e.g., APR/12)
    n (int): total number of payments
    '''
    r /= 12 #interest per month
    A = P / ( (1+r)**n-1 ) * (r*(1+r)**n)
    
    return A

def find_optimal_schedule(P,r,n,test_range,M=None):
    '''Creates table to find the optimal overpayment schedule
    '''
    cols = ['Additive Down', 'Total Payment Schedule', 'Total Interest Paid']
    df = pd.DataFrame(columns=cols)
    
    for rng in test_range:
        total_schedule, total_interest = generate_amortization_table(P=P, r=r, n=n, M=M, additive=rng, return_range=True)
        df = pd.concat([df, pd.DataFrame([rng, total_schedule, total_interest], index=cols).T])
    
    df.reset_index(drop=True, inplace=True)
    return df

def generate_amortization_table(P,r,n,M=None,additive=0,return_range=False):
    '''Generate complete amortization schedule
    
    P (int): initial principal
    r (float): interest per period (e.g., APR/12)
    n (int): total number of payments
    M (float, optional): total payment amount
    additive (float, optional): additional monthly principal payment
    '''
    cols = ['Beginning Balance', 'Total Pmt', 'Interest', 'Principal', 'Ending Balance', 'Total Interest']
    df = pd.DataFrame(columns=cols)
    if not M:
        M = calculate_snapshot_monthly(P=P, r=r, n=n)+additive #monthly total (this is constant)
    TI = 0
    
    for i in range(n):
        I = calculate_interest(P=P, r=r)
        TI += I
        P_i = P #initial balance
        pr = M-I #principal
        P -= pr #ending balance

        if P < 0: 
            M = P_i
            pr = M
            P = 0

        tmp = [P_i, M, I, pr, P, TI]
        tmp = [round(j,2) for j in tmp]
        
        df = pd.concat([df, pd.DataFrame(tmp, index=cols).T])

        if P == 0: #break cycle if ends early
            break

    df = df.reset_index(drop=True)
    df.index += 1
    if return_range:
        return max(df.index), TI
    else:
        return df