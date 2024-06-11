# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    from scipy import optimize
    from dateutil.relativedelta import relativedelta
    from datetime import datetime
    import math

    Callable_IG = pd.read_excel(r"C:\Users\LUIS\Documents\MFE\AFP Princing Callable Bonds\6-30-2022\Investment Grade - Callable - 6.30.2022.xlsx",header=1)
    Bullet_IG = pd.read_excel(r"C:\Users\LUIS\Documents\MFE\AFP Princing Callable Bonds\6-30-2022\Investment Grade - Bullet - 6.30.2022.xlsx",header=1)

    Callable_HY = pd.read_excel(r"C:\Users\LUIS\Documents\MFE\AFP Princing Callable Bonds\6-30-2022\High yield - Callable - 6.30.2022.xlsx",header=1)
    Bullet_HY = pd.read_excel(r"C:\Users\LUIS\Documents\MFE\AFP Princing Callable Bonds\6-30-2022\High yield - Bullet - 6.30.2022.xlsx",header=1)

    r = pd.read_excel(r"C:\Users\LUIS\Documents\MFE\AFP Princing Callable Bonds\6-30-2022\r_lattice_vol_0.0208.xlsx", header=None)

    Callable_IG['Credit Spread'] = 0
    Callable_HY['Credit Spread'] = 0

    for j in range(0,len(Callable_HY)):  ## Assigns the credit spread to investment grade bonds from the bullet bond information
        bullet_spreads = Bullet_HY[['Cusip', 'Description', 'Maturity Date', 'OAS']].loc[
            Callable_HY['Description'][j]== Bullet_HY['Description']]
        callable_spreads = Callable_HY[['Cusip', 'Description', 'Maturity Date']].loc[
            Callable_HY['Description'] == Callable_HY['Description'][j]]
        spreads = callable_spreads.merge(bullet_spreads, on=['Cusip', 'Description', 'Maturity Date'],
                                         how='outer')  # Creates spreads dataframe with

        spreads['Maturity Date'] = pd.to_datetime(spreads['Maturity Date'])
        spreads = spreads.sort_values(by='Maturity Date')
        spreads = spreads.set_index('Maturity Date').interpolate(method="linear")
        spreads = spreads.fillna(method="ffill")
        spreads = spreads.fillna(method="bfill")
        spreads = spreads.reset_index(drop='True')  ##Filling the missing credit spreads with the ones there are
        Callable_HY = Callable_HY.reset_index(drop='True')

        spreads = spreads.rename({"OAS": "Credit Spread"}, axis='columns')

        Callable_HY = Callable_HY.set_index('Cusip')
        spreads = spreads.set_index('Cusip')

        Callable_HY.update(spreads)  # updates the Credit Spread Values
        Callable_HY = Callable_HY.reset_index()
        del spreads, callable_spreads, bullet_spreads

    Callable_HY = Callable_HY[Callable_HY['Credit Spread'] != 0]
    Callable_HY = Callable_HY.reset_index(drop='True')

    for i in range(0, len(Callable_IG)):## Assigns the credit spread to investment grade bonds from the bullet bond information
        bullet_spreads = Bullet_IG[['Cusip','Description','Maturity Date', 'OAS']].loc[Bullet_IG['Description'] == Callable_IG['Description'][i]]
        callable_spreads = Callable_IG[['Cusip','Description','Maturity Date']].loc[Callable_IG['Description'] == Callable_IG['Description'][i]]
        spreads = callable_spreads.merge(bullet_spreads, on=['Cusip','Description','Maturity Date'], how='outer')#Creates spreads dataframe with

        spreads['Maturity Date'] = pd.to_datetime(spreads['Maturity Date'])
        spreads = spreads.sort_values(by='Maturity Date')
        spreads = spreads.set_index('Maturity Date').interpolate(method="linear")
        spreads = spreads.fillna(method="ffill")
        spreads = spreads.fillna(method="bfill")
        spreads = spreads.reset_index(drop='True')##Filling missing credit spreads with the ones that are available
        Callable_IG = Callable_IG.reset_index(drop='True')

        spreads = spreads.rename({"OAS": "Credit Spread"}, axis='columns')

        Callable_IG = Callable_IG.set_index('Cusip')
        spreads = spreads.set_index('Cusip')

        Callable_IG.update(spreads)#updates the Credit Spread Values
        Callable_IG = Callable_IG.reset_index()
        del spreads, callable_spreads, bullet_spreads

    Callable_IG = Callable_IG[Callable_IG['Credit Spread'] != 0]
    Callable_IG = Callable_IG.reset_index(drop='True')

    df_IG = Callable_IG
    df_HY = Callable_HY

    df_IG = pd.DataFrame(df_IG)
    df_HY = pd.DataFrame(df_HY)

    df_IG = df_IG[(df_IG['Maturity Date'] < '2040-06-30')] #Pick bonds with Maturity less than 20 years
    df_IG = df_IG.reset_index()

    df_HY = df_HY[(df_HY['Maturity Date'] < '2040-06-30')]  # Pick bonds with Maturity less than 20 years
    df_HY = df_HY.reset_index()

    df_IG['Model_Price'] = 0
    df_IG['Error_Model'] = 0
    df_IG['abs_Error_Model'] = 0# Add columns to callable bonds dataframe

    df_HY['Model_Price'] = 0
    df_HY['Error_Model'] = 0
    df_HY['abs_Error_Model'] = 0  # Add columns to callable bonds dataframe

    present_date = datetime(2022, 6, 30)

    for i in range(0, len(df_IG)):

        maturity_date = df_IG['Maturity Date'][i]
        years = relativedelta(maturity_date, present_date).years# Find the number of months and years between present and maturity of the bond
        months = relativedelta(maturity_date, present_date).months

        cs = df_IG['Credit Spread'][i] * 0.0001
        r_plus_cs = r + cs

        T_cb = years + math.floor(months / 12 * 2) / 2
        T_coupon_before_Maturity = months if months < 6 else months - 6  # Time between last coupon and maturity
        FV = 100
        Coupon = df_IG['Par Wtd Coupon'][i]
        q = .5
        CB = pd.DataFrame(index=np.arange(T_cb * 2 + 1), columns=np.arange(T_cb * 2 + 1))  # creates Callable Bond Matrix
        CB[T_cb * 2] = FV / (1 + r[T_cb * 2]/12)**T_coupon_before_Maturity + Coupon/2  # Assigns (FV + coupon) at the last column of the Callable Bond matrix


        for ii in np.arange(0.5, T_cb + 0.5, 0.5): # Fills the CB matrix backwards
            for jj in np.arange(0, T_cb - ii + 0.5, 0.5):
                CB[(T_cb - ii) * 2][jj*2] = min(FV + Coupon/2, 1/(1 + r_plus_cs[(T_cb - ii) * 2][jj * 2]/2)
                                               * ((q * CB[(T_cb - ii) * 2 + 1][jj * 2]) + ((1 - q) * CB[(T_cb - ii) * 2 + 1][jj * 2 + 1])) + Coupon/2)#Assigns the minimum value between continuation value and exercise value
        df_IG['Model_Price'][i] = CB[0][0]

    for i in range(0, len(df_HY)):

        maturity_date = df_HY['Maturity Date'][i]
        years = relativedelta(maturity_date, present_date).years# Find the number of months and years between present and maturity of the bond
        months = relativedelta(maturity_date, present_date).months

        cs = df_HY['Credit Spread'][i] * 0.0001
        r_plus_cs = r + cs

        T_cb = years + math.floor(months / 12 * 2) / 2
        T_coupon_before_Maturity = months if months < 6 else months - 6  # Time between last coupon and maturity
        FV = 100
        Coupon = df_HY['Par Wtd Coupon'][i]
        q = .5
        CB = pd.DataFrame(index=np.arange(T_cb * 2 + 1), columns=np.arange(T_cb * 2 + 1))  # creates Callable Bond Matrix
        CB[T_cb * 2] = FV / (1 + r[T_cb * 2]/12)**T_coupon_before_Maturity + Coupon/2  # Assigns (FV + coupon) at the last column of the Callable Bond matrix


        for ii in np.arange(0.5, T_cb + 0.5, 0.5): # Fills the CB matrix backwards
            for jj in np.arange(0, T_cb - ii + 0.5, 0.5):
                CB[(T_cb - ii) * 2][jj*2] = min(FV + Coupon/2, (1/(1 + r_plus_cs[(T_cb - ii) * 2][jj * 2]/2)
                                               * ((q * CB[(T_cb - ii) * 2 + 1][jj * 2]) + ((1 - q) * CB[(T_cb - ii) * 2 + 1][jj * 2 + 1])) + Coupon/2))#Assigns the minimum value between continuation value and exercise value
        df_HY['Model_Price'][i] = CB[0][0]

    df_IG['Error_Model'] = df_IG['Model_Price'] - df_IG['Price']
    df_IG['abs_Error_Model'] = abs(df_IG['Error_Model'])
    IG_avg_error = df_IG['abs_Error_Model'].mean()
    IG_std_error = df_IG['abs_Error_Model'].std()
    IG_max_error = df_IG['abs_Error_Model'].max()

    df_HY['Error_Model'] = df_HY['Model_Price'] - df_HY['Price']
    df_HY['abs_Error_Model'] = abs(df_HY['Error_Model'])
    HY_avg_error = df_HY['abs_Error_Model'].mean()
    HY_std_error = df_HY['abs_Error_Model'].std()
    HY_max_error = df_HY['abs_Error_Model'].max()

    df_IG.to_excel(r"C:\Users\LUIS\Documents\MFE\AFP Princing Callable Bonds\6-30-2022\IG_vol_0.0208.xlsx",header=True, index=True)
    df_HY.to_excel(r"C:\Users\LUIS\Documents\MFE\AFP Princing Callable Bonds\6-30-2022\HY_vol_0.0208.xlsx",header=True, index=True)

    print(2)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
