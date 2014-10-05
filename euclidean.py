def euclidean_GCD (a,b): 
	r = max(a,b) - min(a,b)
	if a == 0 and b == 0: 
		return 0
	elif a==0 or b == 0: 
		print "No GCD for", a, b
		return None
	elif min(a,b)%r ==0: 
		return r
	else: 
		return euclidean_GCD(min(a,b), r)

def least_common_multiple(a,b): 
	#Proposition: The least common multiple of a and b is the product of a,b divided by the GCD.
	lcm = (a*b)/euclidean_GCD(a,b)
	return lcm



def main(): 

	print euclidean_GCD(15, 13)
	print euclidean_GCD(17017, 18900)
	print euclidean_GCD(54, 42)
	print euclidean_GCD(462,1071)
	print least_common_multiple(462, 1071)




if __name__ == '__main__':
	main()