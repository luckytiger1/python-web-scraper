with open('combined_csv.csv', 'r') as in_file, open('new_combined_csv.csv', 'w') as out_file:
    seen = set()  # set for fast O(1) amortized lookup
    for line in in_file:
        if line in seen:
            continue  # skip duplicate

        seen.add(line)
        out_file.write(line)
