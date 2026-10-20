import numpy as np 
from sklearn.linear_model import LinearRegression

# 1. provide the training data ( the "experience")
# house sizes (in square feet)
X = np.array([[1500], [1800], [2400], [3000], [3500]])
# house prices (in dollars) 
y = np.array([300000, 350000, 450000, 500000, 600000])  

# 2. choose a model (the "brain")
# linear regression model DRAWS A STRAIT LINE THROUGH THE DATA POINTS TO FIND THE BEST FIT LINE
model = LinearRegression()

# 3. train the model (the "learning" process)
# the AI looks at the data and learns the relationship between house sizes and prices
print("Training the model with the provided data...")
model.fit(X, y)
print("Model training complete!")

#4. make predictions (the "thinking" process)
# let's say we want to predict the price of a house that is 2000 square feet which the model has never seen before 
# 
new_house_size = np.array([[1200]])  
prediction = model.predict(new_house_size)

# output the prediction 
print(f"Predicted price for a {new_house_size[0][0]} ft house: ${prediction[0]:,.2f}")
