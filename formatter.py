import numpy as np
import pandas as pd
import random
import re
#Author: Kekhrie Tsurho

def main():
    
    #Modes: Initial Mode, Merge Mode.
    input_mode = input("Enter the mode: ")
    if input_mode == "-i":
        csv_file = "CSc_144_Fall_2023_grades.csv"
        df, numpy_array = read_csv_file(csv_file) # read csv file function call
        file = create_output_file(df, "output.txt") #Manipulate the data and create output file

    elif input_mode == "-m":
        initial_file = "output.txt"
        csv_file = "CSc_144_Fall_2023_grades_latest.csv"
        df, numpy_array = read_csv_file(csv_file) # read csv file function call
        create_merged_file(df, "merged.txt", initial_file)
    
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
        #For Fall 2023
        #file.write('AssignmentDueDay:-N/A-,08/21,09/01,??/??,??/??,??/??,??/??,09/08,09/15,10/06,10/13,11/03,11/10,12/01,09/22,10/20,11/17\n')

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

                        #Late days
                        late_days = 3
                        for i in range(1, 8):
                            lateness_column = f'Homework #{i} - Lateness (H:M:S)'
                            if lateness_column in df.columns and row[lateness_column] != "00:00:00":
                                late_days -= 1

                        late_days = max(0, late_days)
                        data_points = [str(late_days), background_survey]

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
                            # Case for late days, check properly
                            if late_days == 0 and hw_column in df.columns:
                                data_points.append('0') 
                                
                            elif hw_column in df.columns:
                                data_points.append(str(int(row[hw_column])).rjust(max_width) if not pd.isna(row[hw_column]) else '0'.rjust(max_width))
                        
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

                        # print(data_points)
                else:
                    # If the student is not found in the new CSV file, just append the line without modification
                    print(constructed_email)
                    merged_data.append(line)
                    if idx+1 < len(existing_data):  # Check if next line exists
                        next_line = existing_data[idx+1]
                        scores = next_line.strip().split()
                        # Determine the missing scores count.
                        total_expected_scores = expected_scores_count(df)
                        missing_scores_count = total_expected_scores - len(scores)
                        scores.extend(['0'] * missing_scores_count)
                        merged_scores = ' '.join(scores)
                        
                        merged_data.append(f"{merged_scores}\n")

            else:
            # If the line does not contain student information, just append the line without modification
                line = line.strip() + "\n"
    return merged_data

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
                labels.append(f'{i}{versions_found[0].ljust(5)}')
            else:
                labels.append(f'QUIZ{i}')
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
