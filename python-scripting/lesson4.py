status_code = int( input("enter an HTTP status code: "))

if status_code == 200:
	print("The request success")
else:
	print("the response was not http 200")
