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
                },{
                    "id": 2,
                    "name": "User",
                    "email": "User@dlfs.com",
                    "password": "user123",
                    "role": "user"
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


### CLASSES TO DEFINE USERS, ITEMS, AND CLAIMS ###
'''
Contains classes to represent users, items, and claims in the DLFS system

'''
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

### Manages all interactions with users, items, and claims ###

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
            if "email" in user and "password" in user:
                if user["email"] == email and user["password"] == password:
                    print("Login successful")
                    return user  # Return user dictionary if credentials match
        print("Invalid email or password.")
        return None

    def add_user(self, user_id, name, email, password, role):
        """Add a new user to the system"""
        new_user = User(user_id, name, email, password, role)
        users = load_data("users.json")
        users.append(new_user.__dict__)
        save_data("users.json", users)
        self.users = load_data("users.json")


    def report_item(self, name, description, location, item_type, user_id):
        """Create and store a new reported item"""
        item = ReportedItem(name, description, location, item_type)
        self.items.append(item.__dict__)  # Store as dictionary
        self.save_all()
        return item.item_id  # Return generated item ID


### ITEM SEARCH FUNCTIONS ###
    def search_items_name(self, keyword):
        """Search items by keyword in the name"""
        return [item for item in self.items if keyword.lower() in item["name"].lower()]
    
    def search_items_location(self, location):
        """Search items by location"""
        return [item for item in self.items if location.lower() in item['location'].lower()]

    def search_items_type(self, item_type):
        """Search items by item type (lost or found)""" 
        return [item for item in self.items if item_type.lower() in item['item_type'].lower()]


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


# MENUS #
'''
Contains all menu functions for user and admin interactions with the user interface

'''

class DLFSUI:
    """User Interface for the DLFS system"""
    def __init__(self, controller):
        self.controller = DLFSController()
    
    def print_items(self, results):
        """Helper function to print a list of items"""
        if results:
            print("\n--- Items Found ---")
            for item in results:
                print(f"Item ID: {item['item_id']}, Name: {item['name']}, Location: {item['location']}, Type: {item['item_type']}, Status: {item['status']}")
        else:
            print("No items found matching this search.")
       
    def report_lost_item(self, user):
        # Report lost item
        name = input("Item name: ")
        desc = input("Description: ")
        loc = input("Location: ")
        item_id = self.controller.report_item(name, desc, loc, "lost", user["id"])
        print(f"Lost item reported. Item ID: {item_id}")

    def report_found_item(self, user):
        # Report found item
        name = input("Item name: ")
        desc = input("Description: ")
        loc = input("Location: ")
        item_id = self.controller.report_item(name, desc, loc, "found", user["id"])
        print(f"Found item reported. Item ID: {item_id}")


    def claim_item(self, user, item_id=None):
                        # Claim an item
        if item_id is None:
            item_id = input("Enter Item ID to claim: ")
        else:
            claim_id = self.controller.claim_item(user["id"], item_id)
            print(f"Claim submitted. Claim ID: {claim_id}")



### SEARCH MENU FUNCTIONS ###

    def search_menu(self):
        # Search menu options
        print("\n--- Search Menu ---")
        print("1. View All Items")
        print("2. Search by Keyword")
        print("3. Search by Location")
        print("4. Search by Item Type")
        return(input("Choose an option: "))

    def view_all_items(self):
                            # View all items
        if self.controller.items:
            print("\n--- All Items ---")
            self.print_items(self.controller.items)                    
        else:
            print("No items in the system.")

    def search_by_keyword(self, keyword=None):
                        # Search by keyword
        if keyword == None:              
            keyword = input("Enter keyword: ")
        else:
            results = self.controller.search_items_name(keyword)
            self.print_items(results)

    def search_by_location(self, location=None):
                            # Search by location
        if location == None:
            location = input("Enter location: ")
        else:
            results = self.controller.search_items_location(location)
            self.print_items(results)

    def search_by_type(self, t=None):
                    # Search by item type (lost or found)
        if t == None:
            print("Choose type: 1 for Lost, 2 for Found")
            t = input("Enter choice: ")
        else:
            item_type = "lost" if t == "1" else "found"
            results = self.controller.search_items_type(item_type)
            self.print_items(results)




### MENU FOR USERS ###

    def user_menu(self,user):
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
                self.report_lost_item(user)

            elif choice == "2":
                self.report_found_item(user)

            elif choice == "3":
                sub_choice = self.search_menu()

                if sub_choice == "1":
                    self.view_all_items()

                elif sub_choice == "2":
                    self.search_by_keyword()
                    
                elif sub_choice == "3":
                    self.search_by_location()

                elif sub_choice == "4":
                    self.search_by_type()

                else:
                    print("Invalid choice. Please try again.")


            elif choice == "4":
                self.claim_item(user)

            elif choice == "5":
                # Logout
                break

### MENU FUNCTIONS FOR ADMINS ###

    def approve_claim(self):
        claim_id = input("Enter Claim ID: ")
        if self.controller.approve_claim(claim_id):
            print("Claim approved.")
        else:
            print("Claim not found.")

    def add_user(self):
        id = input("User ID (numeric): ")
        name = input("Name: ")
        email = input("Email: ")
        password = input("Password: ")
        role = input("Role (user/admin): ").lower()
        if role not in ["user", "admin"]:
            print("Invalid role. Defaulting to user.")
            role = "user"
        # Add user through controller    
        self.controller.add_user(id, name, email, password, role)

### MENU FOR ADMINS ###

    def admin_menu(self, admin):
        """Menu for admins"""
        while True:
            print("\n--- Admin Menu ---")
            print("1. Approve Claim")
            print("2. Add user")
            print("3. Logout")
            choice = input("Choose an option: ")

            if choice == "1":
                self.approve_claim()
            elif choice == "2":
               self.add_user()
            elif choice == "3":
                break




    def main_menu(self):
        """Main menu for login and exit"""
        while True:
            print("\n--- DLFS Main Menu ---")
            print("1. Login")
            print("2. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                email = input("Email: ")
                password = input("Password: ")
                user = self.controller.login(email, password)
                if user:
                    # Show menu based on role
                    if user["role"] == "admin":
                        self.admin_menu(user)
                    else:
                        self.user_menu(user)
                else:
                    print("Invalid credentials.")
            elif choice == "2":
                break


class TestSystem:
    """Test class for the DLFS system"""
    def __init__(self, controller, ui, user, admin):
        self.controller = DLFSController()
        self.ui = DLFSUI(controller)
        self.user = user
        self.admin = admin

    def test_login(self):
        self.controller.login(self.user["email"], self.user["password"])
        self.controller.login(self.admin["email"], self.admin["password"])
        self.controller.login(self.user["email"], "wrongpassword")
        self.controller.login(self.admin["email"], "wrongpassword")

    def test_print_items(self):
        self.controller.report_item("TestItem", "A test item", "TestLocation", "lost", self.user["id"])
        self.ui.print_items(self.controller.items)

    
    def test_report_lost_item(self):
        self.controller.report_item("LostItem", "A lost item", "LostLocation", "lost", self.user["id"])

    def test_report_found_item(self):
        self.controller.report_item("FoundItem", "A found item", "FoundLocation", "found", self.user["id"])

    def test_view_all_items(self):
        print("\n[Test] View All Items:")
        self.ui.view_all_items()

    def test_search_by_keyword(self):
        print("\n[Test] Search by Keyword:")
        # Add a test item
        self.controller.report_item("TestItem", "A test item", "TestLocation", "lost", self.user["id"])
        self.ui.search_by_keyword("TestItem")

    def test_search_by_location(self):
        print("\n[Test] Search by Location:")
        # Add a test item
        self.controller.report_item("TestItem2", "Another test item", "SpecialLocation", "found", self.user["id"])
        self.ui.search_by_location("SpecialLocation")

    def test_search_by_type(self):
        print("\n[Test] Search by Type:")
        # Add a test item
        self.controller.report_item("TestItem3", "Type test item", "TypeLocation", "lost", self.user["id"])
        self.ui.search_by_type("1")  # '1' for lost

    def run_all_login_tests(self):
        self.test_login()

    def run_all_item_tests(self):
        self.test_report_found_item()
        self.test_report_lost_item()

    def run_all_ui_tests(self):
        self.test_print_items()
        self.test_view_all_items()
        self.test_search_by_keyword()
        self.test_search_by_location()
        self.test_search_by_type()
        print("\nAll UI tests completed successfully.")

    def run_all_tests(self):
        self.run_all_login_tests()
        self.run_all_item_tests()
        self.run_all_ui_tests()






def main():
##MAIN MENU##
    UI = DLFSUI(DLFSController())
    UI.main_menu()


if __name__ == "__main__":
    main()
