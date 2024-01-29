# Grade Management System for CSc 144

## Introduction
Introduction to the Grade formatting System for CSc 144, Fall 2023. This Python-based application is designed to streamline the process of managing and processing student grades. It provides functionalities such as reading grades from CSV files, merging data from various sources, handling exceptions for late submissions, and calculating aggregate quiz scores.

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


## How to Run:

### Initial Run:
1. Download a copy of the CSV file from Gradescope, located in the assignment tab. This should be the grade file, containing all of the greades of the students, not just the grade of one homework assignment.
2. Ensure that the CSV columns are formatted as shown in the provided screenshot, with headers: 'First Name', 'Last Name', 'SID', and 'Email'. If the format matches, proceed to the next steps. Otherwise, adjust the code within the `extract_student_data()` function accordingly.
3. In the `main()` function, within the `-i` mode, update the `csv_file` variable to match the name of your downloaded CSV file.
4. Execute the grading program. When prompted for an input mode, enter `-i`.
5. The program will generate a score file. You can customize the output file's name in the `main()` function under the `-i` mode called `output_name`

### Merge Step:
1. For merging, open the `main()` function and locate the `-m` mode. Set the `initial_file` variable to the name of the initial score file from the initial run (or any score file).
2. Download the latest CSV file from Gradescope and update the `csv_file` variable in the `main()` function under `-m` mode to the new CSV file's name.
3. This mode will output another file. You can rename this output file within the `-m` mode section called `merged_final`.

### Aggregate Step:
1. To aggregate quiz scores, select a pre-existing score file.
2. In the `main()` function, under the `-a` mode, enter the name of your score file.
3. Set the `lowest_n` value to indicate how many of the lowest scores should be dropped.
4. Running this mode will produce a final score file. You can set your preferred name for this output within the `-a` mode section.

**Note**: Always verify the CSV format and the file paths before running each step to ensure the grade formatting functions correctly.

## Exceptions for Homeworks
To accommodate situations where students are marked late but should not be penalized with reduced late days, the grading formatter includes an `exceptions` dictionary. This dictionary provides a way to specify exceptions for individual homework assignments.

The `exceptions` dictionary uses the homework number as the key, and the value is an array containing the email IDs of students who are exempt from late penalties for that particular homework.

### Example:
```python
exceptions = {
    'Homework #2': ['abc@arizona.edu', 'def@arizona.edu'],
    'Homework #7': ['qwe@arizona.edu']
}
```

## Missing:
- There are two aspects of the grading program that are partially completed. The first is the meta-data dates for assignments, these have to be put in manually everytime the grading program runs and a score file is outputted. 
- The second is spacing between scores for quizzes, homeworks, and exams. 

