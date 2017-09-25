
# class Test:
#     def __init__(self, test_number):
#         self.secret = test_number
#         print("created")
#
#     def __getattribute__(self, item):
#         if item == "secret":
#             return None
#         return super().__getattribute__(item)
#
#     def print_number(self):
#         print(self.secret)


def test():
    try:
        return True
    finally:
        print("hi")


def main():
    print(",".join(["{}", "{}"]).format("hi", "lol"))


if __name__ == '__main__':
    main()


