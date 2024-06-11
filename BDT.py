# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    from scipy import optimize
    from dateutil.relativedelta import relativedelta
    from datetime import datetime

    spot_rates = pd.read_excel(r"C:\Users\LUIS\Documents\MFE\AFP Princing Callable Bonds\6-30-2022\Spot_rates 6-30-2022.xlsx")#Reads effective yield or risk-free rate file depending on the model.
    spot_rates = pd.DataFrame(spot_rates)

    spot_rates = spot_rates.interpolate()

    spot_rates['D(T)'] = 0
    spot_rates['Sum_D(T)'] = 0

    spot_rates['D(T)'][0] = 1 / (1 + spot_rates['Spot Rate'][0]/100 / 2)**(spot_rates['T'][0]*2) #Fills the first D(T) value
    spot_rates['Sum_D(T)'][0] = spot_rates['D(T)'][0]

    #Fills the other D(T) values from the given spot rates
    for ii in range(1, len(spot_rates)):
        spot_rates['D(T)'][ii] = (100 - spot_rates['Sum_D(T)'][ii-1] * spot_rates['Spot Rate'][ii] / 2) \
                                    / (spot_rates['Spot Rate'][ii]/2+100)
        spot_rates['Sum_D(T)'][ii] = spot_rates['Sum_D(T)'][ii-1] + spot_rates['D(T)'][ii]
    _D_T = spot_rates[['T', 'D(T)']]

    _D_T = pd.DataFrame(_D_T)

    T = 20
    step = 0.5
    r0 = spot_rates['Spot Rate'][0]
    vol = 0.25 # vol of Treasury Yield or of B or AA indices

    r = pd.DataFrame(index=np.arange(T * 2), columns=np.arange(T * 2))  # creates short rate matrix
    r[0][0] = spot_rates['Spot Rate'][0]  # assigns first value in short rate matrix

    for ii in np.arange(0.5, T, 0.5):

        D_T = pd.DataFrame(index=np.arange(ii * 2 + 1),
                           columns=np.arange(ii * 2 + 1))  # Creates D_T matrix to calculate the D(T) value
        D_T[ii * 2][:] = 1  # Assigns 1 at the last column of D_T matrix

        ind = ii * 2 - 1 # ind: next to last column before in D_T matrix


        def find_r_star(a):
            r[ind][0] = a
            for kk in np.arange(1, ii * 2):  # Fills last column of r matrix
                r[ind][kk] = r[ind][kk - 1] * np.exp(-2 * vol * step ** 0.5)

            for i in np.arange(0, ii * 2):
                for j in np.arange(0, ind - i+1):  # Fills the D_T matrix with short rate matrix
                    D_T[ind - i][j] = 0.5 * (D_T[ind - i + 1][j] / (1 + r[ind - i][j] / 2)) + \
                                        0.5 * (D_T[ind - i + 1][j + 1] / (1 + r[ind - i][j] / 2))

            result = abs(D_T[0][0] - _D_T.iloc[int(ii*2-1), 1])
            return result


        first_guess = 0.02  # First guess for r*

        res = optimize.minimize(find_r_star, first_guess)

        r[ind][0] = res.x[0]
        for kk in np.arange(1, ii * 2):  # Fills last column of r matrix
            r[ind][kk] = r[ind][kk - 1] * np.exp(-2 * vol * step ** 0.5)

        for j in np.arange(0, ii * 2):  # Fills the D_T matrix with short rate matrix
            for i in np.arange(0, ii * 2 - 1):
                D_T[ind - i][j] = 0.5 * (D_T[ind - i + 1][j] / (1 + r[ind - i][j] / 2)) + 0.5 * (
                                    D_T[ind - i + 1][j + 1] / (1 + r[ind - i][j] / 2))

    cs = pd.DataFrame(index=np.arange(T * 2+1), columns=np.arange(T * 2 + 1))  # creates credit spread matrix
    cs[0][0] = 0.025
    corr = -0.16 # Correlation coefficient between interest rate and credit spread

    for i in np.arange(1, T * 2):
        cs[i][0] = cs[i - 1][0] + (r[i][0] - r[i - 1][0]) / r[i - 1][0] \
                   * corr * cs[i - 1][0]
        for j in np.arange(1, i + 1):  # Fills the D_T matrix with short rate matrix
            cs[i][j] = cs[i - 1][j - 1] + (r[i][j] - r[i - 1][j - 1]) / r[i - 1][j - 1] \
                       * corr * cs[i - 1][j - 1]

    r_plus_cs = r + cs

    r.to_excel(r"C:\Users\LUIS\Documents\MFE\AFP Princing Callable Bonds\6-30-2022\r_lattice_vol_0.0208.xlsx", header=False, index=False) # Stores the interest rate lattice

    print(2)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
