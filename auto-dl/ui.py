"""
Terminal-Based Neural Network Trainer
User Interface Component
"""

from simple_term_menu import TerminalMenu

class UserInterface:
    """
    Handles user interaction through terminal menus and text inputs.
    """
    
    def show_main_menu(self):
        """Display the main menu options."""
        options = ["Train New Model", "Load Existing Model", "Exit"]
        terminal_menu = TerminalMenu(
            options, 
            title="Neural Network Trainer - Main Menu",
            menu_cursor="▶ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black")
        )
        menu_entry_index = terminal_menu.show()
        return options[menu_entry_index]
    
    def get_csv_filename(self):
        """Get CSV filename from user."""
        return self.get_input("Enter CSV filename: ")
    
    def select_target_feature(self, columns):
        """Allow user to select a target feature from available columns."""
        terminal_menu = TerminalMenu(
            columns, 
            title="Select Target Feature",
            menu_cursor="▶ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black")
        )
        menu_entry_index = terminal_menu.show()
        return columns[menu_entry_index]
    
    def select_input_features(self, columns, default_selected=None):
        """
        Allow user to select multiple input features from available columns.
        Returns a list of selected column names.
        """
        if default_selected is None:
            default_selected = [True] * len(columns)
            
        terminal_menu = TerminalMenu(
            columns,
            title="Select Input Features (Space to toggle, Enter to confirm)",
            menu_cursor="▶ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black"),
            multi_select=True,
            preselected_entries=default_selected
        )
        
        selected_indices = terminal_menu.show()
        if selected_indices is None:  # User pressed Esc
            return []
            
        return [columns[i] for i in selected_indices]
    
    def confirm_action(self, message):
        """Ask for user confirmation."""
        options = ["Yes", "No"]
        terminal_menu = TerminalMenu(
            options, 
            title=message,
            menu_cursor="▶ ",
            menu_cursor_style=("fg_green", "bold"),
            menu_highlight_style=("bg_green", "fg_black")
        )
        menu_entry_index = terminal_menu.show()
        return menu_entry_index == 0
    
    def get_input(self, prompt):
        """Get text input from user."""
        return input(prompt)
    
    def get_integer_input(self, prompt, min_val=None, max_val=None):
        """Get integer input from user within specified range."""
        while True:
            try:
                value = int(input(prompt))
                if min_val is not None and value < min_val:
                    print(f"Please enter a value >= {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Please enter a value <= {max_val}")
                    continue
                return value
            except ValueError:
                print("Please enter a valid integer")
    
    def get_float_input(self, prompt, min_val=None, max_val=None):
        """Get float input from user within specified range."""
        while True:
            try:
                value = float(input(prompt))
                if min_val is not None and value < min_val:
                    print(f"Please enter a value >= {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Please enter a value <= {max_val}")
                    continue
                return value
            except ValueError:
                print("Please enter a valid number")
    
    def display_message(self, message):
        """Display a message to the user."""
        print(message)
    
    def display_title(self, title):
        """Display a title with decoration."""
        print("\n" + "=" * len(title))
        print(title)
        print("=" * len(title) + "\n")