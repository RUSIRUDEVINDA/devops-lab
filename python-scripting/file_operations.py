# Write: create the file or replace its existing contents
with open("server.txt", "w", encoding="utf-8")as file:
	file.write("web-01\n")
	file.write("db-01\n")

# Read: get all the text from the file
with open("server.txt", "r", encoding="utf-8")as file:
	content = file.read()

print("=== Original content ===")
print(content) 

# Append: add text at the end without removing existing content.
with open("server.txt", "a", encoding="utf-8")as file:
	file.write("monitoring-01\n")

# Read line by line
print("after appending\n")
with open("server.txt", "r", encoding="utf-8")as file:
	for line in file:
		print(line, end="")


#read exsisitng files
with open("server.txt", "r", encoding="utf-8")as file:
	lines = file.readlines()

#update file
with open("server.txt", "w", encoding="utf-8")as file:
	for i in lines:
		if i.rstrip("\n")=="web-01":
			file.write("web-02\n")
		else:
			file.write(i)
print("\nupdated\n")

#after update
with open("server.txt", "r", encoding="utf-8")as file:
	content = file.read()

print("after update\n")
print(content)

#remove line
with open("server.txt", "r", encoding="utf-8")as file:
	lines = file.readlines()
with open("server.txt", "w", encoding="utf-8")as file:
	for i in lines:
		if i.rstrip("\n")!="db-01":	
			file.write(i)

print("\nline removed\n")

#after removal
print("after removal\n")

with open("server.txt", "r", encoding="utf-8")as file:
	content = file.read()

print(content)
