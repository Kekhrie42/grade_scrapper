import numpy as np
import pandas as pd
#Author: Kekhrie Tsurho

def main():

    df, numpy_array = read_csv_file() # read csv file function call

    file = create_output_file(df, numpy_array) #Manipulate the data and create output file 

    write_to_dir(file) # write to directory function call

# read csv file
def read_csv_file():
    csv_file = "CSc_144_Spring_2023_grades.csv"
    df = pd.read_csv(csv_file)
    #print(df)
    numpy_array = df.values
    #print(numpy_array)
    return df, numpy_array


def create_output_file(df, numpy_array):
    #Create a file with the following:
        #For each student create name, NETID, status, and grade
        #For the above information, add scores:
            #Late days, Quiz 0, Quiz 1-13..., HW1-7..., Exam 1-3, Final Exam

    filename = "output.txt" #File Name Creation
    with open(filename, 'w') as file: #Metadata
        # Write hardcoded metadata
        file.write('StudentFamilyName,')
        file.write('StudentGivenName,')
        file.write('UofArizona NetID,')
        file.write('*,')
        file.write('GRDSHTID\n')
        file.write('ScoresListHere\n')
    
        for _, student in df.iterrows(): #Iterate through each student and add their information into the file
            file.write(extract_student_data(df, student))

    

def extract_student_data(df, row):
        # Extract the meta-data
        meta_data = f"{row['Name']},{row['SID']}"

        # Extract 'Background Survey' and adjust based on requirements
        if not pd.isna(row['Background Survey']) and row['Background Survey'] == 0.0:
            background_survey = '1'
        elif pd.isna(row['Background Survey']):
            background_survey = '0'
        else:
            background_survey = str(int(row['Background Survey']))
        # Extract the other required columns
        data_points = [
            #TODO: Implement late days
            background_survey, #0 if there and nothing of not there
            str(int(row['Practice Quiz (Quiz 0)'])) if not pd.isna(row['Practice Quiz (Quiz 0)']) else '0'
        ]
        
        # Add Quizes, Homeworks, Exams, and Final Exam
        for i in range(14):  # Adjust this to the number of quizzes 
            versions = ['A', 'B', 'C', 'D', '']  # Assuming up to D versions and a possibility of no version
            valid_versions = [version for version in versions if f'Quiz #{i}{version}' in df.columns]
            quiz_scores = []
            
            for version in valid_versions:
                col_name = f'Quiz #{i}{version}'
                if col_name in df.columns and not pd.isna(row[col_name]): #If submission exists
                    quiz_scores.append(str(int(row[col_name])))
                else:
                    quiz_scores.append('0')  # if submission doesn't exist

            max_score = max(quiz_scores, default='0') if quiz_scores else ''  # Take the maximum score among the valid versions
            data_points.append(max_score)


        data_points.extend(str(int(row[f'Homework #{i}'])) if not pd.isna(row[f'Homework #{i}']) else '0' for i in range(1, 8))
        data_points.append('')
        data_points.extend(str(int(row[f'Exam #{i}'])) if not pd.isna(row[f'Exam #{i}']) else '0' for i in range(1, 4))
        data_points.append('')
        data_points.append(str(int(row['Final Exam'])) if not pd.isna(row['Final Exam']) else '0')
        
        
        # Convert all points to string
        data_points_str = ' '.join(data_points)
        
        return f"{meta_data}\n{data_points_str}\n"
        

#TODO
def write_to_dir(file):
    #Write the file to the directory
    return 0

main()
