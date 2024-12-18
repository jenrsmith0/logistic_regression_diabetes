import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import category_encoders as ce
from sklearn.metrics import confusion_matrix
from sklearn.metrics import d2_absolute_error_score
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import root_mean_squared_error

if __name__ == '__main__':
    dataset = pd.read_csv("diabetes_prediction_dataset.csv")
    print(dataset.head())

    # get shape of the data and column names
    print(dataset.shape)
    col_names = dataset.columns
    print(col_names)

    # print a summary of our dataset
    print(dataset.info())

    # print how many different labels gender contains and the frequency
    categorical = ['gender', 'hypertension', 'heart_disease', 'smoking_history', 'diabetes']
    for col in categorical:
        print(col, ' contains ', len(dataset[col].unique()), ' labels')
        print(dataset[col].value_counts())

    numerical = ['age', 'bmi', 'HbA1c_level', 'blood_glucose_level']
    for col in numerical:
        print(dataset[col].describe())
        print("mode\t\t", dataset[col].mode())
        print("range\t\t", dataset[col].max() - dataset[col].min())
        print("variance\t\t", dataset[col].var())
        print("iqr\t\t", dataset[col].quantile(0.75) - dataset[col].quantile(0.25))
        
        bp_fig = plt.figure()
        bp = dataset.boxplot(column=col)
        bp.set_title('Box Plot of ' + col)
        bp.set_ylabel(col)
        bp_fig.savefig(col + "boxplot.png")

        hist_fig = plt.figure()
        hist = dataset[col].hist(bins=10)
        hist.set_title('Histogram of ' + col)
        hist.set_ylabel(col)
        hist_fig.savefig(col + "histogram.png")

    bmi_value_count = dataset['bmi'].value_counts()
    total_bmi_outliers = 0
    
    for bmi, count in bmi_value_count.items():
        if (bmi > 38.5 or bmi < 14.71):
            total_bmi_outliers += 1
    
    print("Total outliers for BMI ", total_bmi_outliers)

    # Update the smoking history to be just three labels now
    def change_smoking_history(smoking_history):
        if smoking_history in ['never', 'No Info']:
            return 'never'
        elif smoking_history in ['ever', 'former', 'not current']:
            return 'former'
        elif smoking_history == 'current':
            return 'current'

    dataset['smoking_history'] = dataset['smoking_history'].apply(change_smoking_history)

    # Remove the other gender
    dataset = dataset[dataset['gender'] != 'Other']
    
    x = dataset.drop(['diabetes'], axis=1)
    y = dataset['diabetes']

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 0)

    encoding = ce.OrdinalEncoder(cols=['smoking_history', 'gender'])

    x_train = encoding.fit_transform(x_train)
    x_test = encoding.transform(x_test)

    # Logistic Regression

    logreg = LogisticRegression(solver = "liblinear", random_state = 0)
    logreg.fit(x_train, y_train)

    y_pred_test = logreg.predict(x_test)
    print('Logistic Regression Model accuracy score: {0:0.4f}'. format(accuracy_score(y_test, y_pred_test)))

    y_pred_train = logreg.predict(x_train)
    print('Logistic Regression Model accuracy score: {0:0.4f}'. format(accuracy_score(y_train, y_pred_train)))

    scores = cross_val_score(logreg, x_train, y_train, cv = 5, scoring='accuracy')
    print('Logistic Regression cross validation scores:{}'.format(scores))

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred_test)
    print(y_test.value_counts())
    print(pd.DataFrame(data=y_pred_test).value_counts())
    
    cm_matrix = pd.DataFrame(data=cm, columns=['Predict Negative:0', 'Predict Positive:1'],
                            index=['Actual Negative:0', 'Actual Positive:1'])
    heatmap = sns.heatmap(cm_matrix, annot=True, fmt='d', cmap='YlGnBu')
    fig = heatmap.get_figure()
    fig.savefig("confusion_matrix.png")

    TN = cm[0,0]
    TP = cm[1,1]
    FP = cm[0,1]
    FN = cm[1,0]

    accuracy = (TP + TN) / float(TP + TN + FP + FN)
    print('Accuracy : {0:0.4f}'.format(accuracy))

    sensitivity = TP / float(TP + FN)
    print('Sensitivity : {0:0.4f}'.format(sensitivity))

    precision = TP / float(TP + FP)
    print('Precision : {0:0.4f}'.format(precision))

    specificity = TN / float(TN + FP)
    print('Specificity : {0:0.4f}'.format(specificity))

    f1_score = 2 * ((precision * sensitivity)/(precision + sensitivity))
    print('F1 Score : {0:0.4f}'.format(f1_score))

    # Linear Regression
    linreg = LinearRegression().fit(x_train, y_train)

    y_pred_test = linreg.predict(x_test)
    print('Linear Regression Model D2 absolute error score: {0:0.4f}'. format(d2_absolute_error_score(y_test, y_pred_test)))

    y_pred_train = linreg.predict(x_train)
    print('Linear Regression Model D2 absolute error score: {0:0.4f}'. format(d2_absolute_error_score(y_train, y_pred_train)))

    scores = cross_val_score(linreg, x_train, y_train, cv = 5, scoring='d2_absolute_error_score')
    print('Cross validation scores:{}'.format(scores))

    print('Linear Regression Model mean absolute error score: {0:0.4f}'. format(mean_absolute_error(y_test, y_pred_test)))
    print('Linear Regression Model mean squared error score: {0:0.4f}'.format(mean_squared_error(y_test, y_pred_test)))
    print('Linear Regression Model root mean squared error score: {0:0.4f}'.format(root_mean_squared_error(y_test, y_pred_test)))
