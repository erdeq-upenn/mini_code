import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Download Titanic dataset (from seaborn or Kaggle)
url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
df = pd.read_csv(url)

# Select useful features
features = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare", "Embarked"]
target = "Survived"
df = df[features + [target]]

# Handle missing values
df["Age"].fillna(df["Age"].median(), inplace=True)
df["Embarked"].fillna(df["Embarked"].mode()[0], inplace=True)

# Encode categorical columns
for col in ["Sex", "Embarked"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])

# Split data
X = df[features].values
y = df[target].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalize
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Convert to tensors
X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.long)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.long)

print("Train shape:", X_train.shape)

class TitanicNN(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 2)  # 2 output classes: Survived / Not survived
        )

    def forward(self, x):
        return self.net(x)

model = TitanicNN(X_train.shape[1])
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

epochs = 100
for epoch in range(epochs):
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 10 == 0:
        with torch.no_grad():
            preds = model(X_train).argmax(dim=1)
            acc = (preds == y_train).float().mean().item()
        print(f"Epoch {epoch+1:3d}/{epochs}, Loss: {loss.item():.4f}, Train Acc: {acc:.3f}")

with torch.no_grad():
    y_pred = model(X_test).argmax(dim=1)
    test_acc = (y_pred == y_test).float().mean().item()
print(f"✅ Test Accuracy: {test_acc:.3f}")

# Example: 3rd class, female, age 25, 0 siblings/spouse, 0 parents, fare=7.25, embarked='S'
sample = [[3, 0, 25, 0, 0, 7.25, 2]]  # 0=female, Embarked: S=2
sample = scaler.transform(sample)
sample_tensor = torch.tensor(sample, dtype=torch.float32)

with torch.no_grad():
    pred = model(sample_tensor).argmax(dim=1).item()
print("🎯 Prediction:", "Survived" if pred == 1 else "Did not survive")
