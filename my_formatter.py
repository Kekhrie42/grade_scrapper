"""
Grade Management System for CSc 144, Fall 2023

This module provides functionalities for managing and processing student grades for CSc 144.
It supports reading grades from CSV files, merging grade data, handling exceptions for late submissions,
and aggregating quiz scores.

Functions:
    main(): The main function to run the grade management system.
    aggregate_quizzes(initial_file, lowest_n, df): Aggregates quiz scores, dropping the lowest n scores.
    create_merged_file(df, filename, initial_file): Merges grade data from different sources.
    merge_data(df, existing_data): Helper function to merge data from a DataFrame and a text file.
    populate_scores(dict_scores, scores): Populates the scores for the merged data.
    populate_quizzes(dict_scores, scores, df): Populates quiz scores in the merged data.
    populate_homeworks(dict_scores, scores, df, start): Populates homework scores in the merged data.
    populate_exams(dict_scores, scores, df, start): Populates exam scores in the merged data.
    number_of_quizzes(df): Counts the number of quizzes based on DataFrame columns.
    number_of_homeworks(df): Counts the number of homeworks based on DataFrame columns.
    number_of_exams(df): Counts the number of exams based on DataFrame columns.
    number_of_final_exam(df): Checks if there's a final exam based on DataFrame columns.
    expected_scores_count(df): Counts the expected number of scores based on DataFrame columns.
    read_csv_file(csv_file): Reads a CSV file and returns a DataFrame and a NumPy array.
    create_output_file(df, filename, merge_mode=False): Creates an output file with student grade data.
    write_metadata_to_file(df, file): Writes metadata to the output file.
    extract_student_data(df, row): Extracts and formats student data for the output file.

Variables:
    exceptions (dict): Dictionary of students exempt from late homework penalties.

Author:
    Kekhrie Tsurho
"""

import numpy as np
import pandas as pd
import random
import re
import math
from datetime import datetime, timedelta


# Exception dictionary, if a student is exempt from submitting their homework late without incurring any penalties.
exceptions = {

}

def main():
    
    #Modes: Initial Mode, Merge Mode.
    input_mode = input("Enter the mode: ")
    if input_mode == "-i":
        csv_file = "CSc_144_Fall_2023_grades.csv" #csv file to read
        output_name = "output.txt" #output file name
        df, numpy_array = read_csv_file(csv_file) # read csv file function call
        file = create_output_file(df, output_name) #Manipulate the data and create output file

    elif input_mode == "-m":
        initial_file = "merged.txt" #initial file to merge with
        csv_file = "CSc_144_Fall_2023_grades_final_exam.csv" #csv file to read and merge
        merged_final = "mergedFinal.txt" #output file name
        df, numpy_array = read_csv_file(csv_file) # read csv file function call
        create_merged_file(df, merged_final, initial_file)

    elif input_mode == "-a":
        lowest_n = 4
        initial_file = "mergedFinal.txt" #initial file to merge with
        csv_file = "CSc_144_Fall_2023_grades_final_exam.csv" #csv file to read and merge
        df, numpy_array = read_csv_file(csv_file) # read csv file function call
        aggregate_quizzes(initial_file, lowest_n, df)



def aggregate_quizzes(initial_file, lowest_n, df):
    with open(initial_file, 'r') as file:
        lines = file.readlines()

    # Identify the line that contains quiz labels
    quiz_labels = [label for label in lines if 'AssignmentLabels' in label][0]
    quiz_indices = [i for i, label in enumerate(quiz_labels.split(',')) if 'QUIZ' in label and label != 'QUIZ0']
    # print(quiz_indices, quiz_labels)

    # Process each student's scores
    updated_lines = []
    scores_section = False

    for line in lines:
        if 'ScoresListHere' in line:
            scores_section = True
            updated_lines.append(line)
            continue

        if scores_section:

            if all(x.isdigit() or x.isspace() or x == ',' for x in line):
                scores = line.split()
                end_index = 3 + number_of_quizzes(df)
                quiz_scores = [int(scores[i]) for i in range(3, end_index) if int(scores[i]) <= 10]
                quiz_scores.sort(reverse=True)  # Sort scores in descending order

                # Drop the n lowest scores
                quiz_scores = quiz_scores[:len(quiz_scores) - lowest_n]

                # Update the quiz scores in the original data
                updated_quiz_score = sum(quiz_scores)
                for i in sorted(quiz_indices, reverse=True):
                    del scores[i]  # Remove individual quiz scores
                scores.insert(quiz_indices[0], str(updated_quiz_score))
                
                updated_line = ' '.join(scores)
                updated_lines.append(updated_line+"\n")
            else:
                # Non-score lines are added as is (Homework and Exams)
                updated_lines.append(line)
        else:
            # Lines outside the scores section are added as is (Initial ones before quiz labels)
            updated_lines.append(line)

    # Write the concatenated scores to a new file
    with open('mergedQ.txt', 'w') as out_file:
        for score in updated_lines:
            out_file.write(score)



def create_merged_file(df, filename, initial_file):

    # Read the existing file data (assuming it's a text file with a specific format)
    with open(initial_file, 'r') as file:
        existing_data = file.readlines()
    
    with open(filename, 'w') as file: #Metadata
        #metadata
        file.write('Class: CSc 144, Discrete Math for CS I\n')
        file.write('Section: 002\n')
        file.write('Offered: Fall,2023\n')
        file.write('CategorySortOrder: PROG,HMWK,QUIZ,EXAM,FINL\n')
        file.write('DropLowestInTheseCategories: None\n')
        file.write('ReplaceLowExamWithFinal: Yes\n')
        file.write('ApplyLetterGradePenalty: No\n')
        file.write('FinalExamWeight: 14\n')
        file.write('LetterGradeCutoffs: 89.5,79.5,69.5,59.5\n')
        file.write('\n')

        write_metadata_to_file(df,file)

        file.write('StudentFamilyName,')
        file.write('StudentGivenName,')
        file.write('UofArizona NetID,')
        file.write('*,')
        file.write('GRDSHTID\n')
        file.write('ScoresListHere\n')
        # Get merged data lines
        merged_data_lines = merge_data(df, existing_data)

        # Write merged data lines to file
        
        for line in merged_data_lines:
            file.write(line)

def merge_data(df, existing_data):
    merged_data = []
    start_merging = False
    late_threshold = timedelta(minutes=6) ##Late day time threshold

    for idx, line in enumerate(existing_data):
        if 'ScoresListHere' in line:
            # This line indicates the start of the scores section in the file
            start_merging = True
            continue
        
        if start_merging:
            parts = line.strip().split(',')
            #if student data
            if len(parts) >= 3 and not parts[0].replace(' ', '').isnumeric() and not parts[1].replace(' ', '').isnumeric():
                netID = str(parts[2]).strip()  # Assuming the netID is in the third column
                constructed_email = f"{netID}@arizona.edu"
                constructed_email_alternative = f"{netID}@email.arizona.edu"

                if (constructed_email in df['Email'].values) or (constructed_email_alternative in df['Email'].values):

                        if constructed_email_alternative in df['Email'].values:
                            constructed_email = constructed_email_alternative
                        row = df[df['Email'] == constructed_email].iloc[0]

                        #Background Survey
                        if 'Background Survey' in df.columns:
                            if not pd.isna(row['Background Survey']):
                                background_survey = '1'
                            else:
                                background_survey = '0'
                        else:
                            background_survey = '0'

                        data_points = [background_survey]
                    
                        late_days = 3

                        #Practice Quiz
                        if 'Quiz #0 (Practice Quiz)' in df.columns:
                            data_points.append(str(int(row['Quiz #0 (Practice Quiz)'])) if not pd.isna(row['Quiz #0 (Practice Quiz)']) else '0')

                        max_width = 2
                        for i in range(14):
                            quiz_column = f'Quiz #{i}'
                            if any(quiz_column + version in df.columns for version in ['A', 'B', 'C', 'D', '']):
                               scores = [int(row[quiz_column + version]) for version in ['A', 'B', 'C', 'D', ''] if quiz_column + version in df.columns and not pd.isna(row[quiz_column + version])]                               
                               max_score = max(scores, default=0)
                               data_points.append(str(max_score).rjust(max_width))
                                
                        for i in range(1, 8):  # Homeworks
                            hw_column = f'Homework #{i}'
                            lateness_column = f'Homework #{i} - Lateness (H:M:S)'
                            if hw_column in df.columns and lateness_column in df.columns:
                                lateness_str = row[lateness_column]
                                lateness_parts = lateness_str.split(':')
                                lateness_timedelta = timedelta(
                                hours=int(lateness_parts[0]),
                                minutes=int(lateness_parts[1]),
                                seconds=int(lateness_parts[2])
                            )
                                is_late = lateness_timedelta >= late_threshold
                                
                                # Check if the current student is exempted from this homework
                                is_exempt = hw_column in exceptions and row['Email'] in exceptions[hw_column]
                                
                                # If homework is submitted and it's late
                                if not pd.isna(row[hw_column]) and is_late and not is_exempt:
                                    
                                    # print("Late:", constructed_email, row["First Name"], row["Last Name"], lateness_str, hw_column)
                                    # If they have used all their late days
                                    if late_days == 0:
                                        deducted_score = 50 - int(row[hw_column])
                                        reduced_score = max(0, 38 - deducted_score)
                                        data_points.append(str(int(reduced_score)).rjust(max_width))
                                        # print("Grade Reduction", constructed_email, row["First Name"], row["Last Name"],lateness_str, hw_column)
                                    
                                    # Any other late submissions
                                    else:
                                        data_points.append(str(int(row[hw_column])).rjust(max_width))

                                    late_days -= 1
                                    late_days = max(0, late_days)
                                # If homework is not submitted late or not submitted at all or is exempted
                                else:
                                    data_points.append(str(int(row[hw_column])).rjust(max_width) if not pd.isna(row[hw_column]) else '0'.rjust(max_width))

                        data_points.insert(0,str(late_days))

                        for i in range(1, 4):  # Exams
                            exam_column = f'Exam #{i}'
                            if exam_column in df.columns:
                                data_points.append(str(int(row[exam_column])).rjust(max_width) if not pd.isna(row[exam_column]) else '0'.rjust(max_width))

                        if 'Final Exam' in df.columns:  # Final Exam
                            max_width = 3
                            final_exam_score = str(int(row['Final Exam'])) if not pd.isna(row['Final Exam']) else '0'
                            data_points.append(str(final_exam_score.rjust(max_width)))

                        merged_data.append(line)

                        # Construct the updated scores line
                        scores_str = ' '.join(data_points)
                        scores_line = f"{scores_str}\n"
                        merged_data.append(scores_line)

                else:
                    print(constructed_email) ##All dropped students

                    merged_data.append(line)
                    if idx + 1 < len(existing_data):  # Check if next line exists
                        next_line = existing_data[idx + 1]
                        scores = next_line.strip().split()
                        # print(scores)
                        dict_scores = {'init':[],'quizzes':[], 'homeworks':[], 'exams':[]}
                        dict_scores['init'] = scores[:3]
                        total_expected_scores = expected_scores_count(df)
                        

                        last_quiz = populate_quizzes(dict_scores, scores, df)
                        last_hw = populate_homeworks(dict_scores, scores, df, last_quiz+1)
                       
                        populate_exams(dict_scores, scores, df, last_hw)
                        scores = populate_scores(dict_scores, scores)
                        
                        # Initialize formatted_scores list
                        formatted_scores = []

                        # Special handling to strip and format the first and second scores
                        if scores:
                            formatted_scores.append(scores[0].strip())  # Add the first score
                            if len(scores) > 1:
                                formatted_scores.append(scores[1].strip())  # Add the second score

                        # Right-align the remaining scores
                        for score in scores[2:]:
                            formatted_scores.append(score.rjust(max_width))

                        # Joining scores with a space
                        formatted_score_line = ' '.join(formatted_scores)

                        # Append the formatted score line to merged_data
                        merged_data.append(formatted_score_line +  "\n"  )
 
            else:
            # If the line does not contain student information, just append the line without modification
                line = line.strip() + "\n"
    return merged_data


def populate_scores(dict_scores, scores):
    scores = []
    for key in dict_scores:
        scores.extend(dict_scores[key])
    return scores

def populate_quizzes(dict_scores, scores, df):
    last_quiz_index = 2  # Starting index for quizzes in the scores list
    for i in range(number_of_quizzes(df)):
        if last_quiz_index < len(scores) - 1 and int(scores[last_quiz_index + 1]) <= 10:
            dict_scores['quizzes'].append(scores[last_quiz_index + 1])
            last_quiz_index += 1
        else:
            dict_scores['quizzes'].append('0')
    return last_quiz_index

def populate_homeworks(dict_scores, scores, df, start):
    # Score range for homeworks - assuming homework scores have a known range
    homework_score_range = (0, 50)

    # Populate homeworks
    hw_count = 0
    for i in range(start, len(scores)):
        score = int(scores[i])
        if homework_score_range[0] <= score <= homework_score_range[1]:
            dict_scores['homeworks'].append(scores[i])
            hw_count += 1
        elif hw_count >= number_of_homeworks(df):
            # Stop if we've added the expected number of homework scores
            break

    # Add '0' for any missing homeworks
    for _ in range(number_of_homeworks(df) - hw_count):
        dict_scores['homeworks'].append('0')
    return start + hw_count

def populate_exams(dict_scores, scores, df, start):
    # Calculate the remaining space available for exam scores
    current_length = len(dict_scores['init']) + len(dict_scores['quizzes']) + len(dict_scores['homeworks'])
    remaining_length = expected_scores_count(df) - current_length

    # Check if there is any space left for exam scores
    if remaining_length > 0:
        # Populate exams
        exam_count = 0
        for i in range(start, len(scores)):
            if exam_count < remaining_length:
                dict_scores['exams'].append(scores[i])
                exam_count += 1
            else:
                break

        # Fill in missing exam scores with '0'
        while exam_count < min(number_of_exams(df), remaining_length):
            dict_scores['exams'].append('0')
            exam_count += 1


def number_of_quizzes(df):
    return sum(1 for i in range(14) if any(f'Quiz #{i}' + version in df.columns for version in ['A', 'B', 'C', 'D', '']))

def number_of_homeworks(df):
    return sum(1 for i in range(1, 8) if f'Homework #{i}' in df.columns)

def number_of_exams(df):
    return sum(1 for i in range(1, 4) if f'Exam #{i}' in df.columns)


def number_of_final_exam(df):
    return sum(1 if 'Final Exam' in df.columns else 0)



def expected_scores_count(df):
    count = 3  # Background Survey, late days and quiz 0
    count += sum(1 for i in range(14) if any(f'Quiz #{i}' + version in df.columns for version in ['A', 'B', 'C', 'D', '']))
    count += sum(1 for i in range(1, 8) if f'Homework #{i}' in df.columns)
    count += sum(1 for i in range(1, 4) if f'Exam #{i}' in df.columns)
    count += 1 if 'Final Exam' in df.columns else 0
    return count

# read csv file
def read_csv_file(csv_file):
    df = pd.read_csv(csv_file)
    #print(df)
    numpy_array = df.values
    #print(numpy_array)
    return df, numpy_array

def create_output_file(df, filename, merge_mode=False):
    #Create a file with the following:
        #For each student create name, NETID, status, and grade
        #For the above information, add scores:
            #Late days, Quiz 0, Quiz 1-13..., HW1-7..., Exam 1-3, Final Exam
    with open(filename, 'w') as file: #Metadata
        #metadata
        file.write('Class: CSc 144, Discrete Math for CS I\n')
        file.write('Section: 002\n')
        file.write('Offered: Fall,2023\n')
        file.write('CategorySortOrder: PROG,HMWK,QUIZ,EXAM,FINL\n')
        file.write('DropLowestInTheseCategories: None\n')
        file.write('ReplaceLowExamWithFinal: Yes\n')
        file.write('ApplyLetterGradePenalty: No\n')
        file.write('FinalExamWeight: 14\n')
        file.write('LetterGradeCutoffs: 89.5,79.5,69.5,59.5\n')
        file.write('\n')

        write_metadata_to_file(df,file)
        #For Fall 2023
        #file.write('AssignmentDueDay:-N/A-,08/21,09/01,??/??,??/??,??/??,??/??,09/08,09/15,10/06,10/13,11/03,11/10,12/01,09/22,10/20,11/17\n')

        file.write('StudentFamilyName,')
        file.write('StudentGivenName,')
        file.write('UofArizona NetID,')
        file.write('*,')
        file.write('GRDSHTID\n')
        file.write('ScoresListHere\n')
        
        if merge_mode == False:
            for _, student in df.iterrows(): #Iterate through each student and add their information into the file
                file.write(extract_student_data(df, student))

def write_metadata_to_file(df, file):
   
    # Predefined constants
    quizPoints = 10
    quizWeight = 2
    HWPoints = 50
    HWWeight = 4
    examPoints = 85
    examWeight = 14
    
    # Helper function to check column existence
    def column_exists(prefix, num, version=''):
        return f'{prefix} #{num}{version}' in df.columns

    labels = ['LDAYS', 'SURVY', 'QUIZ0']
    points = ['3', '1', '20']
    weights = ['0', '0', '0']
    duedays = ['-N/A-', '01/11', '01/13']
    
    # Check for Quizzes
    for i in range(1, 13):  # Adjust the range depending on max number of quizzes
        versions_found = [version for version in ['A', 'B', 'C', 'D', ''] if column_exists("Quiz", i, version)]
        if versions_found:
            if(i>=10):
                letter = chr(65 + i - 10)
                label = f'QUIZ{letter}'
            else:
                label = f'QUIZ{i}'

            labels.append(label)
            points.append(str(quizPoints))
            weights.append(str(quizWeight))
            duedays.append('-N/A-')  # Placeholder due day. Update accordingly.
        

    
    # Check for Homeworks
    for i in range(1, 8):  # Adjust the range depending on max number of homeworks
        if column_exists("Homework", i):
            labels.append(f'HMWK{i}')
            points.append(str(HWPoints))
            weights.append(str(HWWeight))
            duedays.append('-N/A-')  # Placeholder due day. Update accordingly.
    
    # Check for Exams
    for i in range(1, 4):  # Adjust the range depending on max number of exams
        if column_exists("Exam", i):
            labels.append(f'EXAM{i}')
            points.append(str(examPoints))
            weights.append(str(examWeight))
            duedays.append('-N/A-')  # Placeholder due day. Update accordingly.
    

    # Find the maximum width from AssignmentLabels for alignment
    max_width = max(map(len, labels))
    
    # Right align the values except for labels
    points = [point.rjust(max_width) for point in points]
    weights = [weight.rjust(max_width) for weight in weights]
    duedays = [dueday.rjust(max_width) for dueday in duedays]

    # Write the metadata to file
    file.write('AssignmentLabels: ' + ','.join(labels) + '\n')
    file.write('AssignmentPoints: ' + ','.join(points) + '\n')
    file.write('AssignmentWeight: ' + ','.join(weights) + '\n')
    file.write('AssignmentDueDay: ' + ','.join(duedays) + '\n')
    file.write('AssignmentLateBy: ' + ','.join(['-N/A-'.rjust(max_width) for _ in labels]) + '\n\n')

def extract_student_data(df, row):
    # Extract the meta-data, name, SID, status, and 6-Digit ID
    random_number = random.randint(100000, 999999)
    status = 'C'

    StudentGivenName = 16  # specify the maximum length for first and middle names
    StudentFamilyName = 17  # specify the maximum length for last name

    if 'Name' in df.columns:
        name = row['Name'].split(' ')
        last_name = name[-1][:StudentFamilyName]  # Trim the last name if necessary
        first_middle_names = ' '.join(name[:-1])[:StudentGivenName]  # Trim the first and middle names if necessary
    elif 'First Name' in df.columns and 'Last Name' in df.columns:
        first_middle_names = row['First Name'][:StudentGivenName]  # Trim the first name if necessary
        last_name = row['Last Name'][:StudentFamilyName]  # Trim the last name if necessary
    else:
        # Handle the case where neither naming convention is present
        first_middle_names = ''
        last_name = ''

    netID_length = len('UofArizona NetID')  # Replace 'len(UofArizona NetID)' with the actual maximum length allowed for netIDs
    netID = str(row['Email']).split('@')[0][:netID_length]

    meta_data = f"{last_name.ljust(StudentFamilyName)},{first_middle_names.ljust(StudentGivenName)},{netID.ljust(16)},{status},{str(random_number)}"

    # Extract 'Background Survey' and adjust based on requirements
    if 'Background Survey' in df.columns:
        if  not pd.isna(row['Background Survey']):
            background_survey = '1'
        elif pd.isna(row['Background Survey']):
            background_survey = '0'
        else:
            background_survey = str(int(row['Background Survey']))
    else:
        background_survey = '0'

    # Case for late days. Only takes into consideration the homeworks
    late_days = 3
    for i in range(1,8):
        lateness_column = f'Homework #{i} - Lateness (H:M:S)'
        if lateness_column in df.columns and row[lateness_column] != "00:00:00":
            late_days -=1

    late_days = max(0, late_days)
    data_points = [str(late_days), background_survey]  # Added a whitespace

    if 'Quiz #0 (Practice Quiz)' in df.columns:
        data_points.append(str(int(row['Quiz #0 (Practice Quiz)'])) if not pd.isna(row['Quiz #0 (Practice Quiz)']) else '0')
    # data_points.append(' ')  # Added a whitespace for quizzes

    max_width = 1
    for i in range(14):  # Check for existence of quiz columns
        quiz_column = f'Quiz #{i}'
        if any(quiz_column + version in df.columns for version in ['A', 'B', 'C', 'D', '']):
            scores = [int(row[quiz_column + version]) for version in ['A', 'B', 'C', 'D', ''] if quiz_column + version in df.columns and not pd.isna(row[quiz_column + version])]
            max_score = max(scores, default=0)
            data_points.append(str(max_score).rjust(max_width))
    # data_points.append('')  # Added a whitespace for homeworks

    for i in range(1, 8):  # Homeworks
        hw_column = f'Homework #{i}'
        if hw_column in df.columns:
            data_points.append(str(int(row[hw_column])).rjust(max_width) if not pd.isna(row[hw_column]) else '0'.rjust(max_width))
    # data_points.append('')  # Added a whitespace for exams

    for i in range(1, 4):  # Exams
        exam_column = f'Exam #{i}'
        if exam_column in df.columns:
            data_points.append(str(int(row[exam_column])).rjust(max_width) if not pd.isna(row[exam_column]) else '0'.rjust(max_width))
    # data_points.append('')  # Added a whitespace for final exam

    if 'Final Exam' in df.columns:  # Final Exam
        max_width = 3
        final_exam_score = str(int(row['Final Exam'])) if not pd.isna(row['Final Exam']) else '0'
        data_points.append(final_exam_score.rjust(max_width))

    data_points_str = ' '.join(data_points)

    return f"{meta_data}\n{data_points_str}\n"
main()
