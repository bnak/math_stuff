#write a func to print all prime nums up to and including the input parameter

def generate_primes(num): 
	primes = [2,3]
	for i in range (3, num+1):
		num_is_prime = True
		for item in primes: 
			if i % item == 0:
				num_is_prime = False

		if num_is_prime == True:
			primes.append(i)

	return primes

def main():

	print generate_primes(17)
	print generate_primes(111)




if __name__ == '__main__':
	main()
