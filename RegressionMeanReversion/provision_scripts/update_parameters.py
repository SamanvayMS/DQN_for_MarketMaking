import sys

def main():
    if len(sys.argv) > 0:
        parameters = sys.argv[1]
        parameters = parameters.split('|')
        with open("parameters.txt", "w") as file:
            for parameter in parameters:
                file.write(f'{parameter}\n')
        print("Data written to parameters.txt")
    else:
        print("No input provided")

if __name__ == "__main__":
    main()