

aoo_path = 'aoo.json'



try:
    with open(aoo_path, 'r'):
        print(f"'{aoo_path}' exists.")
except FileNotFoundError:
    print(f"'{aoo_path}' does not exist.")   