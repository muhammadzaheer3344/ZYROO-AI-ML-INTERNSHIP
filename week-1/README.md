# Zyroo AI/ML Internship

## Week 01 - AI/ML Environment Setup

This task establishes and verifies a Python-based AI/ML development environment for the Zyroo AI/ML Internship.

## Tools Used

- Python 3.13
- Git
- Visual Studio Code
- Jupyter
- Project-local virtual environment

## Python Environment

The project uses Python 3.13 and keeps project dependencies isolated from the existing global Python installation.

## Virtual Environment

A project-local virtual environment named `.venv` is used. It is excluded from Git through `.gitignore` and must not be committed.

## Required Libraries

The project requires:

- NumPy
- Pandas
- Matplotlib
- Seaborn
- Scikit-learn
- Jupyter

## Environment Verification

`week-01/environment_test.py` imports the required AI/ML libraries and prints their installed versions.

## Basic ML Test

The verification script uses Scikit-learn's built-in Iris dataset, trains a Logistic Regression classifier, makes predictions, and reports test accuracy. The basic ML test successfully verifies the required environment.

## Project Structure

```text
zyro-aiml-internship/
├── week-01/
│   └── environment_test.py
├── README.md
├── requirements.txt
└── .gitignore
```

## How to Run

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python week-01/environment_test.py
```

To install the listed dependencies in the project environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
