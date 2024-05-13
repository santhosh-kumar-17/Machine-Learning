import threading
import time  # Import the time module for a slight delay

countie = False
count = 10  # Initialize count outside the function
print('If you didnt find the number between 0 - 10 in one attempt Gomma Bomb vedichurum')
def counter():
    global count, countie  # Use global to access and modify count and countie variables
    while not countie and count > 0:  # Add a condition to stop the countdown when countie is True or count becomes 0
        print(f"Countdown: {count}")  # Display the current count
        count -= 1
        time.sleep(1)  # Add a slight delay of 1 second for each count

    if count == 0:
        print("Boom!")  # Display a message when the countdown reaches 0
        print("Ithukae ivlo neram yosikriyae nee lam oom** than laiku")

# Start the counter thread
threading.Thread(target=counter, daemon=True).start()

def till():
    global countie  # Use global to modify countie variable
    print("Guess Your Number : ")
    number = int(input())  # Correct the input syntax
    if number == 10:
        print('Thappichuta da Mayiru')

        countie = True  # Assign True to countie when number is 10
    if number != 10 :
        print('paavam pannita da paavipayalae')
        print('BOOM!!!!!!!! 💣')

        

# Call the till function
till()
