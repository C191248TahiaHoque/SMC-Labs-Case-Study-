import time
def process_a():
    if request_permission('a1'):
        execute_a1()
        update_step()
        time.sleep(1) 
    if request_permission('a2'):
        execute_a2()
        update_step()
        time.sleep(1)
    # Repeat for a3 and a4
