import csv

def main():
    with open('part1.txt', 'r') as f:
        lines1 = [line.strip().split() for line in f if line.strip()]
    
    with open('part2.txt', 'r') as f:
        lines2 = [line.strip().split() for line in f if line.strip()]
        
    print(f"Lines in part 1: {len(lines1)}")
    print(f"Lines in part 2: {len(lines2)}")
    
    if len(lines1) != len(lines2):
        print("Mismatch in lines!")
        
    headers = [
        "Sl No", "Age", "Sex", "BP_systolic", "BP_diastolic", "PR", "Spo2", "Weight", "CP",
        "chol", "Diabetics", "HTN", "Habits", "ECG", "ECHO", "TMT", "CAG", "Target"
    ]
    
    with open('dataset.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i in range(min(len(lines1), len(lines2))):
            row1 = lines1[i]
            row2 = lines2[i]
            # row1 is 9 cols, row2 is 9 cols
            if len(row1) != 9:
                print(f"Row {i} in part1 doesn't have 9 cols: {row1}")
            if len(row2) != 9:
                print(f"Row {i} in part2 doesn't have 9 cols: {row2}")
            writer.writerow(row1 + row2)
            
    print("dataset.csv created successfully.")

if __name__ == '__main__':
    main()
