import json
import os
import pandas as pd

def extract_incorrect_tasks():
    eval_folder = "evals/evals-visidroid"
    files = os.listdir(eval_folder)
    
    print(f"Found {len(files)} evaluation files in {eval_folder}")
    
    incorrect_tasks = []
    all_correct_tasks = []
    
    for file in files:
        if not file.endswith('.json'):
            continue
            
        with open(os.path.join(eval_folder, file)) as f:
            data = json.load(f)
            
        app_name = data['app_name']
        task_desc = data['task_desc']
        hash_id = data['hash']
        evals = data['evals']
        
        # Check if all evaluations are True
        all_correct = all(evals)
        
        task_info = {
            'app_name': app_name,
            'task_desc': task_desc,
            'hash': hash_id,
            'evals': evals,
            'all_correct': all_correct,
            'correct_count': sum(evals),
            'total_actions': len(evals),
            'accuracy': sum(evals) / len(evals) if len(evals) > 0 else 0
        }
        
        if all_correct:
            all_correct_tasks.append(task_info)
        else:
            incorrect_tasks.append(task_info)
    
    print(f"\nResults:")
    print(f"All correct tasks: {len(all_correct_tasks)}")
    print(f"Incorrect tasks: {len(incorrect_tasks)}")
    print(f"Total tasks: {len(all_correct_tasks) + len(incorrect_tasks)}")
    
    # Sort incorrect tasks by accuracy (worst first)
    incorrect_tasks.sort(key=lambda x: x['accuracy'])
    
    print(f"\nIncorrect tasks (sorted by accuracy, worst first):")
    for i, task in enumerate(incorrect_tasks, 1):
        print(f"{i:2d}. {task['app_name']} - {task['task_desc']}")
        print(f"    Hash: {task['hash']}")
        print(f"    Accuracy: {task['accuracy']:.2%} ({task['correct_count']}/{task['total_actions']})")
        print(f"    Evals: {task['evals']}")
        print()
    
    # Save to CSV
    if incorrect_tasks:
        df = pd.DataFrame(incorrect_tasks)
        output_file = "incorrect_tasks.csv"
        df.to_csv(output_file, index=False)
        print(f"Incorrect tasks saved to: {output_file}")
        
        # Also save as JSON for easier viewing
        output_json = "incorrect_tasks.json"
        with open(output_json, 'w') as f:
            json.dump(incorrect_tasks, f, indent=2)
        print(f"Incorrect tasks also saved to: {output_json}")
    
    return incorrect_tasks, all_correct_tasks

if __name__ == "__main__":
    incorrect_tasks, all_correct_tasks = extract_incorrect_tasks()
