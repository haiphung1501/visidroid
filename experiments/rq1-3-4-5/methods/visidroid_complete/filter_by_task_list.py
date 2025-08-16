import pandas as pd
import os

def filter_tasks_by_list():
    # Read the task list from task_name.txt
    with open('task_name.txt', 'r', encoding='utf-8') as f:
        task_list = [line.strip() for line in f.readlines() if line.strip()]
    
    print(f"Loaded {len(task_list)} tasks from task_name.txt:")
    for i, task in enumerate(task_list, 1):
        print(f"{i:2d}. {task}")
    print()
    
    # Read the all_tasks.xlsx file
    df = pd.read_excel('all_tasks.xlsx')
    print(f"Original file has {len(df)} rows")
    
    # Create lowercase versions for case-insensitive matching
    task_list_lower = [task.lower() for task in task_list]
    df_lower = df.copy()
    df_lower['task_desc_lower'] = df['task_desc'].str.lower()
    
    # Filter to keep only rows where task_desc (case-insensitive) is in the task list
    filtered_df = df[df_lower['task_desc_lower'].isin(task_list_lower)]
    
    print(f"After filtering: {len(filtered_df)} rows")
    print()
    
    # Show which tasks were found and which were not (case-insensitive)
    found_tasks_lower = filtered_df['task_desc'].str.lower().unique()
    not_found_tasks = [task for task in task_list if task.lower() not in found_tasks_lower]
    
    print(f"Found {len(found_tasks_lower)} tasks in the Excel file:")
    for i, task in enumerate(filtered_df['task_desc'].unique(), 1):
        print(f"{i:2d}. {task}")
    
    if not_found_tasks:
        print(f"\n{len(not_found_tasks)} tasks NOT found in the Excel file:")
        for i, task in enumerate(not_found_tasks, 1):
            print(f"{i:2d}. {task}")
    
    # Save the filtered data
    output_file = 'all_tasks_filtered.xlsx'
    filtered_df.to_excel(output_file, index=False)
    print(f"\nFiltered data saved to: {output_file}")
    
    return filtered_df

if __name__ == "__main__":
    filtered_df = filter_tasks_by_list()
