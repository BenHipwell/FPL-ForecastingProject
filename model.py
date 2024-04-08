import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
import matplotlib.pyplot as plt

# initial window = 3
data1 = pd.read_csv("datasets/2021-22_GKv4.csv")
data2 = pd.read_csv("datasets/2022-23_GKv4.csv")

# new window datasets
# data1 = pd.read_csv("datasets/window/2021-22_MID_w1.csv")
# data2 = pd.read_csv("datasets/window/2022-23_MID_w1.csv")


data = pd.concat([data1,data2])

# print(len(data))

# for some reason an empty column is created, this removes it
data = data.drop('Unnamed: 0', axis=1)

# print(data.columns)
# print(data.head)

##################################################################################################################################

# drops GK features
data.drop(['saves1','saves2','saves3','penalties_saved1','penalties_saved2','penalties_saved3'], axis=1, inplace=True)

# # drops FPL features
# data.drop(['transfers_in','selected','transfers_out','value'], axis=1, inplace=True)

# # drops social features
# # rant
# data.drop(['rant_sentiment','rant_count'], axis=1, inplace=True)
# # rmt
# data.drop(['rmt_sentiment','rmt_count'], axis=1, inplace=True)
# # twitter
# data.drop(['twitter_sentiment','twitter_count'], axis=1, inplace=True)

##################################################################################################################################

X = data.drop('points', axis=1)
y = data['points']

def train(times, params):

    mse = 0
    rmse = 0
    mae = 0
    r2 = 0
    importance_dict = {}

    for i in range (0,times):
        state = 2 + (10*i)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=state)

        model = xgb.XGBRegressor(**params, tree_method='gpu_hist')

        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        mse += mean_squared_error(y_test, y_pred)
        rmse += mean_squared_error(y_test, y_pred, squared=False)
        mae += mean_absolute_error(y_test, y_pred)
        r2 += r2_score(y_test, y_pred)

        run_importance_dict = model.get_booster().get_score(importance_type="gain")

        for key, value in run_importance_dict.items():
            if key in importance_dict:
                importance_dict[key] = importance_dict[key] + value
            else:
                importance_dict[key] = value


    print("From an average number of runs: " + str(times))
    print(f'MSE: {mse/times:.2f}')
    print(f'RMSE: {rmse/times:.2f}')
    print(f'MAE: {mae/times:.2f}')
    print(f'R-squared: {r2/times:.2f}')


    for key, value in importance_dict.items():
        importance_dict[key] = importance_dict[key] / times


    # plot top features & colour new features
    color_dict = {'selected': 'red', 'value': 'red', 'transfers_in': 'red', 'transfers_out': 'red',
                   'rant_count': 'red', 'rant_sentiment': 'red',
                     'rmt_count': 'red', 'rmt_sentiment': 'red',
                     'twitter_count': 'red', 'twitter_sentiment': 'red'}

    top_items = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:20]
    top_dict = dict(top_items)
    colors = [color_dict.get(feature, 'blue') for feature in top_dict.keys()] 
    plt.bar(range(len(top_dict)), list(top_dict.values()), align='center', color=colors)
    plt.xticks(range(len(top_dict)), list(top_dict.keys()), rotation='vertical')
    plt.show()


# can be used to find improved hyperparameters
def trainCV():

    params = {
    'tree_method': ['gpu_hist'],
    'max_depth': range(1, 10),
    'learning_rate': [0.1, 0.01, 0.001],
    'n_estimators': range(100, 1000, 100),
    'min_child_weight': [1, 5, 10],
    'gamma': [0, 0.1, 0.2, 0.3, 0.4],
    'subsample': [0.5, 0.6, 0.7, 0.8, 0.9],
    'colsample_bytree': [0.5, 0.6, 0.7, 0.8, 0.9],
    'reg_alpha': [0, 0.1, 0.5, 1, 10],
    'reg_lambda': [0, 0.1, 0.5, 1, 10]
    }

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    xgb_model = xgb.XGBRegressor(objective='reg:squarederror', tree_method='gpu_hist')

    rs = RandomizedSearchCV(xgb_model, param_distributions=params, n_iter=100, n_jobs=-1, cv=5, random_state=42)
    rs.fit(X_train, y_train)

    print("Best hyperparameters found: ", rs.best_params_)

    y_pred = rs.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f'MSE: {mse:.2f}')
    print(f'RMSE: {rmse:.2f}')
    print(f'MAE: {mae:.2f}')
    print(f'R-squared: {r2:.2f}')

    
params = {'objective': 'reg:squarederror','n_estimators': 1000,'learning_rate': 0.01,}

train(times=15,params=params)
# trainCV()