buyingdict = {
    'shirt': 17.3,
    'pants': 15.71,
    'boots': 20.35,
    'jacket': 100.50,
    'special': 10000.99,
    'jersey': 60.21
}
cart = []
total = 0

print("------Menu------")
for key, value in buyingdict.items():
    print(f"{key:15}: ${value:.2f}")
print("----------------")

while True:
    buying = input("Enter what you want to buy: (q to quit)").lower()
    if buying == "q" or buying == "quit":
        break
    elif buying in buyingdict:
        cart.append(buying)

print(cart)
print("-------your order-------")
for buy in cart:
    total += buyingdict.get(buy)
    print(f"{buy:15}: ${buyingdict.get(buy):.2f}")
print(f"Total: ${total:.2f}")
print("-----------------------")
