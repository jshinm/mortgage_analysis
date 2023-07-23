# Amortized Loan Simulator
import warnings
import pandas as pd
import matplotlib.pyplot as plt
from kneed import KneeLocator

warnings.filterwarnings("ignore")
pd.set_option("display.max_rows", None)


class LoanCalc:
    def __init__(self, P, r, n, M=None, additive=0, return_range=False):
        self.P = P
        self.r = r
        self.n = n
        self.M = M
        self.additive = additive

    @staticmethod
    def _calculate_interest(P, r):
        """Calculate simple monthly interest payment"""
        return P * r / 12

    @staticmethod
    def _calculate_snapshot_monthly(P, r, n):
        """Calculate amortized monthly payment

        P (int): initial principal
        r (float): interest per period (e.g., APR/12)
        n (int): total number of payments
        """
        # P = self.P
        # r = self.r
        # n = self.n

        r /= 12  # interest per month
        A = P / ((1 + r) ** n - 1) * (r * (1 + r) ** n)

        return A

    def find_optimal_schedule(
        self, search_range=None, M=None, draw_plot=True, max_rows=None
    ):
        """Creates table to find the optimal overpayment schedule"""

        cols = [
            "Additive Down",
            "Total Payment Schedule",
            "Total Interest Paid",
            "Percent Reduced",
        ]
        df = pd.DataFrame(columns=cols)

        if search_range is None:
            maxval = int(self.P / self.n)
            step = int(maxval * 0.1)
            search_range = range(0, maxval, step)

        for rng in search_range:
            total_schedule, total_interest = self.generate_amortization_table(
                additive=rng, return_range=True
            )

            perc_reduced = ((self.n - total_schedule) / self.n) * 100

            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        [rng, total_schedule, total_interest, perc_reduced], index=cols
                    ).T,
                ]
            )

        df.reset_index(drop=True, inplace=True)

        dff = df[["Additive Down", "Percent Reduced"]].to_numpy()
        # param: curve
        # concave detects knees; convex detects elbow
        kl = KneeLocator(
            x=dff[:, 0].tolist(),
            y=dff[:, 1].tolist(),
            S=1,
            curve="concave",
            direction="increasing",
        )

        # plot schedule
        if draw_plot:
            fig, axs = plt.subplots(2, 1, figsize=(6 * 3, 6 * 2))
            df.plot(
                x="Additive Down", y="Total Payment Schedule", kind="bar", ax=axs[0]
            )
            # ax2 = ax.twinx()
            # axs[1].tick_params(axis="y", labelcolor="red")
            df.plot(x="Additive Down", y="Percent Reduced", kind="line", ax=axs[1])
            axs[1].vlines(kl.knee, 0, 100, linestyles="dashed", colors="red")

        return df[:max_rows]

    def generate_amortization_table(self, additive=0, return_range=False):
        """Generate complete amortization schedule

        P (int): initial principal
        r (float): interest per period (e.g., APR/12)
        n (int): total number of payments
        M (float, optional): total payment amount
        additive (float, optional): additional monthly principal payment
        """
        cols = [
            "Beginning Balance",
            "Total Pmt",
            "Interest",
            "Principal",
            "Ending Balance",
            "Total Principal",
            "Total Interest",
            "Percent Paid",
        ]

        P = self.P
        r = self.r
        n = self.n
        M = self.M

        df = pd.DataFrame(columns=cols)
        if not M:
            M = (
                self._calculate_snapshot_monthly(P=P, r=r, n=n) + additive
            )  # monthly total (this is constant)
        TI = 0  # total interest
        PI = 0  # total principal
        P_initial = P  # initial principal balance

        for i in range(n):
            I = self._calculate_interest(P=P, r=r)
            P_i = P  # initial balance
            pr = M - I  # principal
            P -= pr  # ending balance
            TI += I  # total interest
            PI += pr  # total principal
            perc_paid = (PI / P_initial) * 100  # percent principal paid

            if P < 0:
                M = P_i
                pr = M
                P = 0

            tmp = [P_i, M, I, pr, P, PI, TI, perc_paid]
            tmp = [round(j, 2) for j in tmp]

            df = pd.concat([df, pd.DataFrame(tmp, index=cols).T])

            if P == 0:  # break cycle if ends early
                break

        df = df.reset_index(drop=True)
        df.index += 1
        if return_range:
            return max(df.index), TI
        else:
            return df
