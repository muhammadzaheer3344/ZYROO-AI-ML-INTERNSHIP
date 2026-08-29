import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def main():
    print("AI/ML environment verification")
    print(f"NumPy: {np.__version__}")
    print(f"Pandas: {pd.__version__}")
    print(f"Matplotlib: {matplotlib.__version__}")
    print(f"Seaborn: {sns.__version__}")
    print(f"Scikit-learn: {sklearn.__version__}")

    iris = load_iris()
    features_train, features_test, labels_train, labels_test = train_test_split(
        iris.data,
        iris.target,
        test_size=0.2,
        random_state=42,
        stratify=iris.target,
    )

    model = LogisticRegression(max_iter=200)
    model.fit(features_train, labels_train)
    predictions = model.predict(features_test)
    accuracy = model.score(features_test, labels_test)

    print(f"Dataset: Iris ({len(iris.data)} samples, {iris.data.shape[1]} features)")
    print(f"Predictions made: {len(predictions)}")
    print(f"Test accuracy: {accuracy:.2%}")
    print("SUCCESS: The AI/ML environment and basic model are working correctly.")


if __name__ == "__main__":
    main()
