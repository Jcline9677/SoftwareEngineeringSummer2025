import json
import os
import uuid
import random

# === Data Directory ===
DATA_DIR = "data"
# Create the 'data' directory if it does not exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Ensure required JSON files exist (users.json, items.json, claims.json)
# If users.json does not exist, create it with a default admin account
for file in ["users.json", "items.json", "claims.json"]:
    path = os.path.join(DATA_DIR, file)
    if not os.path.exists(path):
        with open(path, "w") as f:
            if file == "users.json":
                # Add a default admin account
                json.dump([{
                    "id": 1,
                    "name": "Admin",
                    "email": "admin@dlfs.com",
                    "password": "admin123",
                    "role": "admin"
                }], f, indent=4)
            else:
                # Initialize empty list for items.json and claims.json
                json.dump([], f, indent=4)


# === Helper Functions for JSON Data ===
def load_data(file_name):
    """Load JSON data from a file and return as Python list"""
    path = os.path.join(DATA_DIR, file_name)
    with open(path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []  # Return empty list if file is empty or corrupted


def save_data(file_name, data):
    """Save Python list as JSON to a file"""
    path = os.path.join(DATA_DIR, file_name)
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


# === Classes ===
class User:
    """Represents a user in the system"""
    def __init__(self, user_id, name, email, password, role="user"):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role  # "user" or "admin"


class Admin(User):
    """Represents an admin user (inherits from User)"""
    def __init__(self, user_id, name, email, password):
        super().__init__(user_id, name, email, password, role="admin")


class ReportedItem:
    """Represents an item that is reported as lost or found"""
    def __init__(self, name, description, location, item_type):
        # Generate short readable ID like ITEM-1234
        self.item_id = f"ITEM-{random.randint(1000, 9999)}"
        self.name = name
        self.description = description
        self.location = location
        self.item_type = item_type  # "lost" or "found"
        self.status = "reported"  # reported, claimed, approved, returned

class Claim:
    """Represents a claim made by a user for a found item"""
    def __init__(self, user_id, item_id):
        # Generate short readable ID like CLM-5678
        self.claim_id = f"CLM-{random.randint(1000, 9999)}"
        self.user_id = user_id
        self.item_id = item_id
        self.status = "pending"  # pending, approved

# === Controller ===
class DLFSController:
    """Main controller to manage users, items, and claims"""
    def __init__(self):
        # Load data from JSON files into memory
        self.users = load_data("users.json")
        self.items = load_data("items.json")
        self.claims = load_data("claims.json")

    def save_all(self):
        """Save all in-memory data back to JSON files"""
        save_data("users.json", self.users)
        save_data("items.json", self.items)
        save_data("claims.json", self.claims)

    def login(self, email, password):
        """Authenticate user by email and password"""
        for user in self.users:
            if user["email"] == email and user["password"] == password:
                return user  # Return user dictionary if credentials match
        return None

    def report_item(self, name, description, location, item_type, user_id):
        """Create and store a new reported item"""
        item = ReportedItem(name, description, location, item_type)
        self.items.append(item.__dict__)  # Store as dictionary
        self.save_all()
        return item.item_id  # Return generated item ID

    def search_items(self, keyword):
        """Search items by keyword in the name"""
        return [item for item in self.items if keyword.lower() in item["name"].lower()]

    def claim_item(self, user_id, item_id):
        """Submit a claim for a found item"""
        claim = Claim(user_id, item_id)
        self.claims.append(claim.__dict__)  # Store as dictionary
        self.save_all()
        return claim.claim_id  # Return claim ID

    def approve_claim(self, claim_id):
        """Approve a pending claim and update item status"""
        for claim in self.claims:
            if claim["claim_id"] == claim_id:
                claim["status"] = "approved"
                # Update item status as claimed
                for item in self.items:
                    if item["item_id"] == claim["item_id"]:
                        item["status"] = "claimed"
                self.save_all()
                return True
        return False


# === Menus ===
controller = DLFSController()


def user_menu(user):
    """Menu for regular users"""
    while True:
        print("\n--- User Menu ---")
        print("1. Report Lost Item")
        print("2. Report Found Item")
        print("3. Search Items")
        print("4. Claim an Item")
        print("5. Logout")
        choice = input("Choose an option: ")

        if choice == "1":
            # Report lost item
            name = input("Item name: ")
            desc = input("Description: ")
            loc = input("Location: ")
            item_id = controller.report_item(name, desc, loc, "lost", user["id"])
            print(f"Lost item reported. Item ID: {item_id}")

        elif choice == "2":
            # Report found item
            name = input("Item name: ")
            desc = input("Description: ")
            loc = input("Location: ")
            item_id = controller.report_item(name, desc, loc, "found", user["id"])
            print(f"Found item reported. Item ID: {item_id}")

        elif choice == "3":
            # Search menu options
            print("\n--- Search Menu ---")
            print("1. View All Items")
            print("2. Search by Keyword")
            print("3. Search by Location")
            print("4. Search by Item Type")
            sub_choice = input("Choose an option: ")

            if sub_choice == "1":
                # View all items
                if controller.items:
                    print("\n--- All Items ---")
                    for item in controller.items:
                        print(f"Item ID: {item['item_id']}, Name: {item['name']}, Location: {item['location']}, Type: {item['item_type']}, Status: {item['status']}")
                else:
                    print("No items in the system.")

            elif sub_choice == "2":
                # Search by keyword
                keyword = input("Enter keyword: ")
                results = controller.search_items(keyword)
                if results:
                    print("\n--- Search Results ---")
                    for item in results:
                        print(f"Item ID: {item['item_id']}, Name: {item['name']}, Location: {item['location']}, Type: {item['item_type']}, Status: {item['status']}")
                else:
                    print("No items found with that keyword.")

            elif sub_choice == "3":
                # Search by location
                location = input("Enter location: ")
                results = [item for item in controller.items if location.lower() in item['location'].lower()]
                if results:
                    print("\n--- Items Found in Location ---")
                    for item in results:
                        print(f"Item ID: {item['item_id']}, Name: {item['name']}, Location: {item['location']}, Type: {item['item_type']}, Status: {item['status']}")
                else:
                    print("No items found in that location.")

            elif sub_choice == "4":
                # Search by item type (lost or found)
                print("Choose type: 1 for Lost, 2 for Found")
                t = input("Enter choice: ")
                item_type = "lost" if t == "1" else "found"
                results = [item for item in controller.items if item['item_type'] == item_type]
                if results:
                    print(f"\n--- {item_type.capitalize()} Items ---")
                    for item in results:
                        print(f"Item ID: {item['item_id']}, Name: {item['name']}, Location: {item['location']}, Status: {item['status']}")
                else:
                    print(f"No {item_type} items found.")

        elif choice == "4":
            # Claim an item
            item_id = input("Enter Item ID to claim: ")
            claim_id = controller.claim_item(user["id"], item_id)
            print(f"Claim submitted. Claim ID: {claim_id}")

        elif choice == "5":
            # Logout
            break


def admin_menu(admin):
    """Menu for admins"""
    while True:
        print("\n--- Admin Menu ---")
        print("1. Approve Claim")
        print("2. Logout")
        choice = input("Choose an option: ")

        if choice == "1":
            claim_id = input("Enter Claim ID: ")
            if controller.approve_claim(claim_id):
                print("Claim approved.")
            else:
                print("Claim not found.")
        elif choice == "2":
            break


def main():
    """Main menu for login and exit"""
    while True:
        print("\n--- DLFS Main Menu ---")
        print("1. Login")
        print("2. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            email = input("Email: ")
            password = input("Password: ")
            user = controller.login(email, password)
            if user:
                # Show menu based on role
                if user["role"] == "admin":
                    admin_menu(user)
                else:
                    user_menu(user)
            else:
                print("Invalid credentials.")
        elif choice == "2":
            break


if __name__ == "__main__":
    main()
