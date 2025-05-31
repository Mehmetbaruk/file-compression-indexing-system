"""
Base module for all menu handlers
"""

class MenuHandler:
    """
    Base class for all menu handlers in the system
    
    This class implements common menu handling functionality
    that all specialized handlers can inherit from.
    """
    def __init__(self):
        """Initialize the menu handler"""
        self.title = "Menu Handler"
        self.options = []
    
    def display_menu(self):
        """Display the menu title and options"""
        print(f"\n{self.title}")
        print("=" * len(self.title))
        
        for i, option in enumerate(self.options, start=1):
            print(f"{i}. {option}")
        print("0. Back")
    
    def handle_choice(self, choice):
        """
        Handle a user's menu selection
        
        Args:
            choice: The user's choice as a string
        """
        try:
            choice = int(choice)
            
            if 1 <= choice <= len(self.options):
                # Call the appropriate handler method
                handler_method = getattr(self, f"_handle_option_{choice}", None)
                
                if handler_method:
                    handler_method()
                else:
                    print(f"Error: Handler for option {choice} not implemented.")
            elif choice != 0:  # 0 is handled by the caller (to exit/go back)
                print(f"Invalid choice. Please select 0-{len(self.options)}")
                
        except ValueError:
            print("Please enter a number.")
    
    def run(self):
        """Run the menu handler in a loop until the user chooses to exit"""
        running = True
        
        while running:
            self.display_menu()
            choice = input(f"Enter your choice (0-{len(self.options)}): ")
            
            if choice == '0':
                running = False
            else:
                self.handle_choice(choice)