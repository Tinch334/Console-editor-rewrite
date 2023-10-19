import time


class TimeCounter:
    def __init__(self, count_number: int, reset_time: int):
        #The number the counter must count to in order to return true.
        self.count_number = count_number
        #How much time, in seconds, it takes for the counter to reset it's count.
        self.reset_time = reset_time

        #The current time and counter values.
        self.current_count = 0
        self.current_time = 0


    #If the specified count has been reached returns True and resets the count, otherwise returns false and increments the count by one.
    def check_count(self) -> bool:
        if self.current_count >= self.count_number - 1:
            self.current_count = 0
            return True

        self.current_count += 1
        self.current_time = time.time()
        return False


    #Returns the number of counts needed to reach the specified count.
    def get_remaining_counts(self) -> int:
        return self.count_number - self.current_count


    #Checks if the counter should be reset, should be called every editor loop.
    def quit_counter_handler(self):
        if time.time() >= self.current_time + self.reset_time:
            self.current_count = 0
            self.current_time = time.time()