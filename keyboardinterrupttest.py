def main():
    while True:
        print("Still running")


try:
    main()
except KeyboardInterrupt:
    print("goodbye")
finally:
    print("Done")
