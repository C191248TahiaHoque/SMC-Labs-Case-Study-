import time
def process_b():
    if request_permission('b1'):
        execute_b1()
        update_step()
        time.sleep(1)
    
    if request_permission('b2'):
        execute_b2()
        update_step()
        time.sleep(1)
    # Repeat for b3 and b4
