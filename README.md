# Grade Management System for CSc 144

## Introduction
Welcome to the Grade Management System for CSc 144, Fall 2023. This Python-based application is designed to streamline the process of managing and processing student grades. It provides functionalities such as reading grades from CSV files, merging data from various sources, handling exceptions for late submissions, and calculating aggregate quiz scores.

## Features
- **CSV File Reading**: Import student grade data from CSV files for easy management and processing.
- **Data Merging**: Merge grade data from different sources, ensuring consistency and accuracy.
- **Late Submission Handling**: Manage exceptions for late homework submissions without manual tracking.
- **Quiz Score Aggregation**: Automatically calculate aggregate quiz scores while allowing the exclusion of the lowest n scores.
- **Comprehensive Output**: Generate detailed output files with student grades, including metadata and formatted score data.

## Installation
To use this system, ensure you have Python installed on your machine. Additionally, the `numpy` and `pandas` packages are required. They can be installed via pip:
```bash
pip install numpy pandas
```

## Input Modes

- **Initial Mode (-i)**: Used for reading and processing grades directly from a CSV file. This mode is the starting point for grade management, where the initial set of student data is read and prepared for further processing.
- **:Merge Mode (-m)**: This mode is designed for combining grade data from an existing file with new data from a CSV file. It's particularly useful for updating or adding new grade information to an already existing dataset.
- **:Aggregation Mode (-a)**: In this mode, quiz scores are processed with an option to drop the lowest scores. It's ideal for optimizing overall student performance by considering their best attempts in quizzes.

