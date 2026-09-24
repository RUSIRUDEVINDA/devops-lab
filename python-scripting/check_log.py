with open("app.log", "r", encoding="utf-8")as file:
	source = file.readlines()

error_count = 0
warning_count = 0

with open("error.log", "w", encoding="utf-8")as file:
	for i in source:
		if "ERROR" in i:
			file.write(i)
			error_count+=1  
		elif "WARNING" in i:
			warning_count+=1

total = error_count + warning_count

print(f"Found {error_count} error lines")
print(f"Found {warning_count} error lines")
print(f"Total is {total}")	


	
