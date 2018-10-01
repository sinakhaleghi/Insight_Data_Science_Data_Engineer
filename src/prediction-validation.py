import sys
import collections
import os


# description: function to veirfy the inputs data is valid
# input: windiow size, stock values and predicted values
# outout: corrected (if needed) windiow size, stock values and predicted values
def verifyInputData(INPUT_PATH_WINDOW, INPUT_PATH_ACTUAL, INPUT_PATH_PREDICTED):
	# verifying the window.txt file exists and is not empty
	if not os.path.exists(INPUT_PATH_WINDOW) or os.path.getsize(INPUT_PATH_WINDOW) == 0:
		print("The window.txt doesn't exit or is empty.")
		win_size = -1
	else:
		# verifying the window size is a positive integer		
		with open(INPUT_PATH_WINDOW, 'r') as win_file:
			win_size = int(win_file.read().strip())
			if win_size <= 0 or win_size % 1 != 0:
				print("The window size value cannot be zero or negative. Only a positive integer is expected.")
				win_size = -1
	# verifying the actual price file exists and is not empty			
	if not os.path.exists(INPUT_PATH_ACTUAL) or os.path.getsize(INPUT_PATH_ACTUAL) == 0:
		print("The actual.txt does not exist or is empty")
		act_price = -1
	else:
		with open(INPUT_PATH_ACTUAL, 'r') as act_file:
			act_price = act_file.readlines()
	# verifying the predicted price file exists and is not empty
	if not os.path.exists(INPUT_PATH_PREDICTED) or os.path.getsize(INPUT_PATH_PREDICTED) == 0:
		print("The predicted.txt does not exist or is empty")
		pred_price = -1
	else:
		with open(INPUT_PATH_PREDICTED, 'r') as pred_file:
			pred_price = pred_file.readlines()
	return win_size, act_price, pred_price


# description: function to return stock prices and line number for a given hour. 
# input: given hour, line number (the last line associated w/ the given hour in the txt file), file
# output: stock price and line number
def getPricePerHour(hour, line_num, file):
    stock_price = {}
    while line_num < len(file):
        temp = file[line_num].strip()
        # skipping the empty lines
        if not temp: 
            line_num += 1
            continue
	    # reading the values from each line
        hr, ticker, price = temp.split('|')
        # verifying the values exits and are in the correct format
        if not hr or not ticker or not price:
        	line_num += 1 
        	continue
        # add hr to the dict as long as it is equal to hour
        if int(hr) == hour:
            stock_price[ticker] = float(price)
            line_num += 1
            continue
        break 
    return stock_price, line_num


# description: function to find matching stock in a specified hour 
#              and return their count and their error. if no match is found, 0 is returned.
# input: actual prices and predeicted prices
# output: sum of error and count
def getErrPerHour(act_prices, pred_prices):
	err_sum = 0
	count = 0
	for ticker, price in pred_prices.items():
		if act_prices[ticker]:
			err_sum += abs(price - act_prices[ticker])
			count += 1
	return err_sum, count


# description: function to convert the average error to the correct format (0.2f)
# input: average error, hour and window size
# output: correct format of average error
def unifyOutputFormat(avg_err, hour, win_size):
	updated_avg_err = '%d|%d|' % (hour - win_size, hour - 1)
	if avg_err == -1:
		updated_avg_err += "NA"
	else:
		updated_avg_err += '{:0.2f}'.format(avg_err)
	return updated_avg_err


# main function
def main():
	# path to the input/output data
	INPUT_PATH_WINDOW = sys.argv[1]
	INPUT_PATH_ACTUAL = sys.argv[2]
	INPUT_PATH_PREDICTED = sys.argv[3]
	OUTPUT_PATH_COMPARISON = sys.argv[4]

	# reading the input files and verifying that they are valid
	win_size, act_price, pred_price = verifyInputData(INPUT_PATH_WINDOW, INPUT_PATH_ACTUAL, INPUT_PATH_PREDICTED)
	if win_size == -1 or act_price == -1 or pred_price == -1:
		print("The input data is not valid. Terminating the process.")
		exit()
	
	# file to store the final results		
	output_file = open(OUTPUT_PATH_COMPARISON, "w")
	
	# in order to store thr errors per hour, a QUEUE is used. each value in the QUEUE consists 
	# of the total error and the counts of same stock prices per hour
	win = collections.deque()
	act_line_num = 0
	pred_line_num = 0
	hour = 1

	while act_line_num < len(act_price):
		# reading the actual/predicted stock prices
		act_prices, act_line_num = getPricePerHour(hour, act_line_num, act_price)
		pred_prices, pred_line_num = getPricePerHour(hour, pred_line_num, pred_price)
		# no predicted stock price available --> no need to compute the error
		if pred_prices:
			temp_err_sum, temp_count = getErrPerHour(act_prices, pred_prices)
		else:
			temp_err_sum, temp_count = 0.0, 0
		if len(win) == win_size:
			tot_sum = sum(i[0] for i in win)
			tot_count = sum(i[1] for i in win)
			avg_err = tot_sum / float(tot_count) if tot_count != 0 else -1
			output = unifyOutputFormat(avg_err,hour, win_size)
			output_file.write(output + "\n")
			win.popleft()

		win.append((temp_err_sum, temp_count))
		hour += 1

	# store the average error in the output file
	tot_sum = sum(i[0] for i in win)
	tot_count = sum(i[1] for i in win)
	avg_err = tot_sum / float(tot_count) if tot_count != 0 else -1
	output = unifyOutputFormat(avg_err, hour, win_size)
	output_file.write(output + "\n")

	output_file.close()

if __name__ == '__main__':
    main()