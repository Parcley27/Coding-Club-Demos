# coding_club_expo.py
# Coding Club Expo Display System
# Built using the existing snake game as base with matching visual style

import pygame
import csv
import os
import random
import sys
from datetime import datetime

# Initialize pygame
pygame.init()

# Set grid dimensions in pixels (matching original snake game)
grid_width = 1200
grid_height = 600

# Number of squares the grid is wide
grid_width_in_squares = 30

# Square size
square_size = grid_width // grid_width_in_squares

# Set window dimensions in pixels
window_width = grid_width
window_height = grid_height + 60

# Constants
snake_speed = 10
max_moves = 5  # Maximum number of moves in the queue

# Try to load window icon (optional - will skip if file doesn't exist)
try:
    window_icon = pygame.image.load("Python Snake Icon.jpg")
    pygame.display.set_icon(window_icon)
except:
    pass  # Continue without icon if file not found

# Defining colors
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
dark_green = pygame.Color(0, 155, 0)
gray = pygame.Color(200, 200, 200)
light_gray = pygame.Color(240, 240, 240)
blue = pygame.Color(0, 100, 200)
green = pygame.Color(0, 200, 0)

# Define a function to get adjusted green color
def adjusted_green_color(index):
    adjustedGreen = 165 + (index * 5)
    if adjustedGreen > 255:
        adjustedGreen = 255
    return pygame.Color(0, adjustedGreen, 0)

# Initialize game window
pygame.display.set_caption('Southridge Coding Club - Snake Game Expo')
game_window = pygame.display.set_mode((window_width, window_height))

# FPS controller
fps = pygame.time.Clock()

# CSV file for storing member information
CSV_FILE = "member_info.csv"

class MemberDatabase:
    """Handles all member data operations including CSV file management"""
    
    def __init__(self):
        self.members = {}  # Dictionary to store member info
        self.load_members()
    
    def load_members(self):
        """Load existing member data from CSV file"""
        if not os.path.exists(CSV_FILE):
            # Create CSV file with headers if it doesn't exist
            with open(CSV_FILE, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Email', 'First Name', 'Last Name', 'Best Score', 'Last Played'])
            return
        
        # Read existing member data
        with open(CSV_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                email = row['Email']
                full_name = f"{row['First Name']} {row['Last Name']}"
                best_score = int(row['Best Score']) if row['Best Score'] else 0
                
                self.members[email] = {
                    'name': full_name,
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'best_score': best_score,
                    'last_played': row['Last Played']
                }
    
    def add_or_update_member(self, email, first_name, last_name, score=0):
        """Add new member or update existing member's information"""
        full_email = f"{email}@southridge.ca"
        full_name = f"{first_name} {last_name}"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if full_email in self.members:
            # Update existing member
            if score > self.members[full_email]['best_score']:
                self.members[full_email]['best_score'] = score
            self.members[full_email]['last_played'] = current_time
        else:
            # Add new member
            self.members[full_email] = {
                'name': full_name,
                'first_name': first_name,
                'last_name': last_name,
                'best_score': score,
                'last_played': current_time
            }
        
        self.save_to_csv()
        return full_name
    
    def get_member(self, email):
        """Retrieve member information by email"""
        full_email = f"{email}@southridge.ca"
        return self.members.get(full_email)
    
    def save_to_csv(self):
        """Save all member data to CSV file"""
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Email', 'First Name', 'Last Name', 'Best Score', 'Last Played'])
            
            for email, data in self.members.items():
                writer.writerow([
                    email,
                    data['first_name'],
                    data['last_name'],
                    data['best_score'],
                    data['last_played']
                ])
    
    def get_leaderboard(self, limit=10):
        """Get top players sorted by best score"""
        sorted_members = sorted(
            self.members.items(),
            key=lambda x: x[1]['best_score'],
            reverse=True
        )
        return sorted_members[:limit]

class InputBox:
    """Creates interactive text input boxes matching the game's visual style"""
    
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = gray
        self.text = ''
        self.placeholder = placeholder
        self.active = False
        self.font = pygame.font.SysFont('Courier New', 24)
    
    def handle_event(self, event):
        """Handle keyboard input and mouse clicks for the input box"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state when clicked
            self.active = self.rect.collidepoint(event.pos)
            self.color = blue if self.active else gray
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                # Remove last character
                self.text = self.text[:-1]
            elif len(self.text) < 20:  # Limit text length
                self.text += event.unicode
    
    def draw(self, screen):
        """Draw the input box with game-style border"""
        # Draw white background
        pygame.draw.rect(screen, white, self.rect)
        # Draw border (thicker when active)
        border_width = 3 if self.active else 2
        pygame.draw.rect(screen, self.color, self.rect, border_width)
        
        # Display text or placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = black if self.text else gray
        
        text_surface = self.font.render(display_text, True, text_color)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 12))

class Button:
    """Creates clickable buttons matching the game's visual style"""
    
    def __init__(self, x, y, width, height, text, color=blue):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont('Courier New', 24)
        self.clicked = False
    
    def handle_event(self, event):
        """Handle button click events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False
    
    def draw(self, screen):
        """Draw the button with game-style appearance"""
        # Draw button background
        pygame.draw.rect(screen, self.color, self.rect)
        # Draw border
        pygame.draw.rect(screen, black, self.rect, 2)
        
        # Center the text on the button
        text_surface = self.font.render(self.text, True, white)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class SnakeGame:
    """Enhanced Snake game based on the original with expo integration"""
    
    def __init__(self):
        self.reset_game()
        self.highscore = 0
    
    def reset_game(self):
        """Reset game to initial state (from original game)"""
        starting_x = 10 * square_size
        starting_y = 8 * square_size
        
        self.snake_position = [starting_x, starting_y]
        self.snake_body = [[starting_x, starting_y], 
                          [starting_x - square_size, starting_y], 
                          [starting_x - (2 * square_size), starting_y]]
        self.fruit_position = self.generate_fruit()
        self.fruit_spawn = True
        self.direction = 'RIGHT'
        self.move_queue = []  # Move queue initialized empty
        self.score = 0
        self.game_over_state = False
    
    def generate_fruit(self):
        """Generate fruit at random location not occupied by snake (from original)"""
        while True:
            new_position = [random.randrange(1, (grid_width // square_size)) * square_size,
                           random.randrange(1, (grid_height // square_size)) * square_size]
            
            if new_position not in self.snake_body:
                return new_position
    
    def handle_input(self, event):
        """Handle keyboard input with move queue system (from original)"""
        if event.type == pygame.KEYDOWN:
            # Add inputs to the move queue
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                if len(self.move_queue) < max_moves:
                    self.move_queue.append('UP')
            
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                if len(self.move_queue) < max_moves:
                    self.move_queue.append('DOWN')
            
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                if len(self.move_queue) < max_moves:
                    self.move_queue.append('LEFT')
            
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                if len(self.move_queue) < max_moves:
                    self.move_queue.append('RIGHT')
    
    def update(self):
        """Update game state each frame (from original game logic)"""
        if self.game_over_state:
            return
        
        # Process move queue (from original)
        if self.move_queue:
            next_move = self.move_queue.pop(0)  # Take the first move in the queue
            if next_move == 'UP' and self.direction != 'DOWN':
                self.direction = 'UP'
            elif next_move == 'DOWN' and self.direction != 'UP':
                self.direction = 'DOWN'
            elif next_move == 'LEFT' and self.direction != 'RIGHT':
                self.direction = 'LEFT'
            elif next_move == 'RIGHT' and self.direction != 'LEFT':
                self.direction = 'RIGHT'
        
        # Move the snake (from original)
        if self.direction == 'UP':
            self.snake_position[1] -= square_size
        elif self.direction == 'DOWN':
            self.snake_position[1] += square_size
        elif self.direction == 'LEFT':
            self.snake_position[0] -= square_size
        elif self.direction == 'RIGHT':
            self.snake_position[0] += square_size
        
        # Snake body growing mechanism (from original)
        self.snake_body.insert(0, list(self.snake_position))
        if self.snake_position[0] == self.fruit_position[0] and self.snake_position[1] == self.fruit_position[1]:
            self.score += 1
            self.fruit_spawn = False
        else:
            self.snake_body.pop()
        
        if not self.fruit_spawn:
            self.fruit_position = self.generate_fruit()
        self.fruit_spawn = True
        
        # Check for collisions (from original)
        if (self.snake_position[0] < 0 or self.snake_position[0] > grid_width - square_size or 
            self.snake_position[1] < 0 or self.snake_position[1] > grid_height - square_size):
            self.game_over_state = True
        
        for block in self.snake_body[1:]:
            if self.snake_position[0] == block[0] and self.snake_position[1] == block[1]:
                self.game_over_state = True
    
    def draw(self, screen):
        """Draw the game using original visual style"""
        # Fill background
        screen.fill(white)
        
        # Draw grid (from original)
        for x in range(0, grid_width, square_size):
            for y in range(0, grid_height, square_size):
                pygame.draw.rect(screen, gray, pygame.Rect(x, y, square_size, square_size), 1)
        
        # Draw snake (from original with gradient colors)
        for i, pos in enumerate(self.snake_body):
            color = dark_green if i == 0 else adjusted_green_color(i)
            pygame.draw.rect(screen, color, pygame.Rect(pos[0], pos[1], square_size, square_size))
        
        # Draw fruit (from original)
        pygame.draw.rect(screen, red, pygame.Rect(self.fruit_position[0], self.fruit_position[1], square_size, square_size))
        
        # Draw bottom info bar (from original style)
        pygame.draw.rect(screen, white, pygame.Rect(0, grid_height, grid_width, 60))
        pygame.draw.line(screen, black, (0, grid_height), (grid_width, grid_height), 2)

class ExpoGameSystem:
    """Main application class that manages all screens and game flow"""
    
    def __init__(self):
        self.database = MemberDatabase()
        self.current_screen = "onboarding"  # Current screen: onboarding, game, leaderboard
        self.current_player_name = ""
        self.current_player_email = ""
        self.snake_game = SnakeGame()
        self.running = True
        
        # Create onboarding screen elements
        self.setup_onboarding_screen()
    
    def setup_onboarding_screen(self):
        """Initialize all onboarding screen input elements"""
        # Input boxes for new member registration
        self.first_name_input = InputBox(100, 200, 250, 50, "First Name")
        self.last_name_input = InputBox(100, 270, 250, 50, "Last Name")
        self.email_input = InputBox(100, 340, 250, 50, "Email (before @)")
        
        # Quick login input
        self.quick_login_input = InputBox(500, 250, 250, 50, "Email (before @)")
        
        # Buttons
        self.register_button = Button(100, 420, 180, 60, "Play Game!", green)
        self.quick_login_button = Button(500, 330, 180, 60, "Quick Login", blue)
        self.leaderboard_button = Button(850, 250, 180, 60, "Leaderboard", gray)
    
    def handle_onboarding_events(self, event):
        """Handle all events on the onboarding screen"""
        # Handle input box events
        self.first_name_input.handle_event(event)
        self.last_name_input.handle_event(event)
        self.email_input.handle_event(event)
        self.quick_login_input.handle_event(event)
        
        # Handle button clicks
        if self.register_button.handle_event(event):
            # Validate full registration form
            if (self.first_name_input.text.strip() and 
                self.last_name_input.text.strip() and 
                self.email_input.text.strip()):
                
                # Register new member or update existing
                self.current_player_name = self.database.add_or_update_member(
                    self.email_input.text.strip(),
                    self.first_name_input.text.strip(),
                    self.last_name_input.text.strip()
                )
                self.current_player_email = self.email_input.text.strip()
                self.start_game()
        
        if self.quick_login_button.handle_event(event):
            # Validate quick login
            if self.quick_login_input.text.strip():
                member = self.database.get_member(self.quick_login_input.text.strip())
                if member:
                    self.current_player_name = member['name']
                    self.current_player_email = self.quick_login_input.text.strip()
                    # Update last played time
                    self.database.add_or_update_member(
                        self.quick_login_input.text.strip(),
                        member['first_name'],
                        member['last_name'],
                        member['best_score']
                    )
                    self.start_game()
        
        if self.leaderboard_button.handle_event(event):
            self.current_screen = "leaderboard"
    
    def start_game(self):
        """Initialize and start the snake game"""
        self.snake_game.reset_game()
        self.current_screen = "game"
    
    def handle_game_events(self, event):
        """Handle events during gameplay"""
        # Handle snake movement
        self.snake_game.handle_input(event)
        
        # Check for game over click to return
        if event.type == pygame.MOUSEBUTTONDOWN and self.snake_game.game_over_state:
            # Save final score and return to onboarding
            if self.current_player_name and self.current_player_email:
                member = self.database.get_member(self.current_player_email)
                if member:
                    self.database.add_or_update_member(
                        self.current_player_email,
                        member['first_name'],
                        member['last_name'],
                        max(self.snake_game.score, member['best_score'])
                    )
            
            # Update highscore for display
            if self.snake_game.score > self.snake_game.highscore:
                self.snake_game.highscore = self.snake_game.score
            
            # Clear inputs and return to onboarding
            self.clear_inputs()
            self.current_screen = "onboarding"
    
    def handle_leaderboard_events(self, event):
        """Handle events on the leaderboard screen"""
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.current_screen = "onboarding"
    
    def clear_inputs(self):
        """Clear all input fields on onboarding screen"""
        self.first_name_input.text = ""
        self.last_name_input.text = ""
        self.email_input.text = ""
        self.quick_login_input.text = ""
        self.current_player_name = ""
        self.current_player_email = ""
    
    def draw_onboarding_screen(self):
        """Draw the main onboarding screen with plain white background"""
        # Draw plain white background
        game_window.fill(white)
        
        # Title section
        title_font = pygame.font.SysFont('Courier New', 60, bold=True)
        subtitle_font = pygame.font.SysFont('Courier New', 36)
        
        title_text = title_font.render("Southridge Coding Club", True, black)
        title_rect = title_text.get_rect(center=(window_width // 2, 80))
        game_window.blit(title_text, title_rect)
        
        subtitle_text = subtitle_font.render("Snake Game Challenge", True, blue)
        subtitle_rect = subtitle_text.get_rect(center=(window_width // 2, 130))
        game_window.blit(subtitle_text, subtitle_rect)
        
        # Section headers
        section_font = pygame.font.SysFont('Courier New', 28, bold=True)
        
        new_member_text = section_font.render("New Member Registration:", True, black)
        game_window.blit(new_member_text, (100, 170))
        
        returning_member_text = section_font.render("Returning Member:", True, black)
        game_window.blit(returning_member_text, (500, 220))
        
        leaderboard_text = section_font.render("View Scores:", True, black)
        game_window.blit(leaderboard_text, (850, 220))
        
        # Draw all input elements
        self.first_name_input.draw(game_window)
        self.last_name_input.draw(game_window)
        self.email_input.draw(game_window)
        self.quick_login_input.draw(game_window)
        
        # Draw buttons
        self.register_button.draw(game_window)
        self.quick_login_button.draw(game_window)
        self.leaderboard_button.draw(game_window)
        
        # Instructions section
        instructions_font = pygame.font.SysFont('Courier New', 18)
        instructions = [
            "Instructions:",
            "• New members: Fill out all fields and click 'Play Game!'",
            "• Returning members: Enter your email and click 'Quick Login'",
            "• Only enter the part before @southridge.ca",
            "• Use WASD or Arrow Keys to control the snake"
        ]
        
        y_pos = 520
        for instruction in instructions:
            text = instructions_font.render(instruction, True, black)
            game_window.blit(text, (100, y_pos))
            y_pos += 22
    
    def draw_game_screen(self):
        """Draw the game screen using original game's drawing method"""
        # Draw the snake game
        self.snake_game.draw(game_window)
        
        # Draw score, controls, and player info in the bottom bar (original style)
        score_font = pygame.font.SysFont('Courier New', 20)
        
        # Player name
        player_surface = score_font.render(f'Player: {self.current_player_name}', True, black)
        game_window.blit(player_surface, (20, window_height - 40))
        
        # Current score
        score_surface = score_font.render(f'Score: {self.snake_game.score}', True, black)
        game_window.blit(score_surface, (300, window_height - 40))
        
        # Controls
        controls_surface = score_font.render("WASD or ARROWS to Move", True, black)
        game_window.blit(controls_surface, (450, window_height - 40))
        
        # Get current player's all-time best score
        player_best_score = 0
        member = self.database.get_member(self.current_player_email)
        if member:
            player_best_score = member['best_score']

        # Get all-time best score across all players
        top_player = self.database.get_leaderboard(1)
        all_time_best = top_player[0][1]['best_score'] if top_player else 0

        # Format the combined high score display
        highscore_text = f"Your Best: {max(self.snake_game.score, player_best_score)}   |   All-Time Best: {max(self.snake_game.score, all_time_best)}"
        highscore_surface = score_font.render(highscore_text, True, black)
        game_window.blit(highscore_surface, (750, window_height - 40))
        
        # Game over overlay (matching original style)
        if self.snake_game.game_over_state:
            # White background box
            pygame.draw.rect(game_window, white, pygame.Rect((window_width / 2) - 300, (window_height / 2) - 200, 600, 400))
            pygame.draw.rect(game_window, black, pygame.Rect((window_width / 2) - 300, (window_height / 2) - 200, 600, 400), 3)
            
            # Game over text
            title_font = pygame.font.SysFont('Courier New', 50, bold=True)
            
            game_over_surface = title_font.render(f"Your Score: {self.snake_game.score}", True, black)
            game_over_rect = game_over_surface.get_rect(center=(window_width / 2, (window_height / 2) - 100))
            game_window.blit(game_over_surface, game_over_rect)
            
            # Continue button
            continue_rect = pygame.Rect((window_width / 2) - 200, (window_height / 2) + 40, 400, 80)
            pygame.draw.rect(game_window, green, continue_rect)
            pygame.draw.rect(game_window, black, continue_rect, 3)
            
            button_font = pygame.font.SysFont('Courier New', 30)
            continue_surface = button_font.render('Click to Continue', True, white)
            continue_text_rect = continue_surface.get_rect(center=continue_rect.center)
            game_window.blit(continue_surface, continue_text_rect)
    
    def draw_leaderboard_screen(self):
        """Draw the leaderboard screen with plain white background"""
        # Plain white background
        game_window.fill(white)
        
        # Title
        title_font = pygame.font.SysFont('Courier New', 60, bold=True)
        title_text = title_font.render("Leaderboard", True, black)
        title_rect = title_text.get_rect(center=(window_width // 2, 80))
        game_window.blit(title_text, title_rect)
        
        # Get top players
        leaderboard = self.database.get_leaderboard(10)
        
        if not leaderboard:
            no_data_font = pygame.font.SysFont('Courier New', 36)
            no_data_text = no_data_font.render("No players yet! Be the first to play!", True, gray)
            no_data_rect = no_data_text.get_rect(center=(window_width // 2, 250))
            game_window.blit(no_data_text, no_data_rect)
        else:
            # Draw leaderboard entries
            y_pos = 180
            entry_font = pygame.font.SysFont('Courier New', 28)
            
            for i, (email, data) in enumerate(leaderboard):
                """
                # Different colors for top 3
                if i == 0:
                    color = pygame.Color(255, 215, 0)  # Gold
                    medal = "🥇"
                elif i == 1:
                    color = pygame.Color(192, 192, 192)  # Silver
                    medal = "🥈"
                elif i == 2:
                    color = pygame.Color(205, 127, 50)  # Bronze
                    medal = "🥉"
                else:
                    color = black
                    medal = f"{i+1}."
                """
                color = black
                medal = f"{i+1}."
                
                rank_text = f"{medal} {data['name']} - {data['best_score']} {'points' if data['best_score'] != 1 else 'point'}"
                rank_surface = entry_font.render(rank_text, True, color)
                
                # Center the text
                rank_rect = rank_surface.get_rect(center=(window_width // 2, y_pos))
                game_window.blit(rank_surface, rank_rect)
                y_pos += 40
        
        # Instructions
        instruction_font = pygame.font.SysFont('Courier New', 24)
        instruction_text = instruction_font.render("Press any key or click to return", True, gray)
        instruction_rect = instruction_text.get_rect(center=(window_width // 2, window_height - 50))
        game_window.blit(instruction_text, instruction_rect)
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events based on current screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.current_screen == "onboarding":
                    self.handle_onboarding_events(event)
                elif self.current_screen == "game":
                    self.handle_game_events(event)
                elif self.current_screen == "leaderboard":
                    self.handle_leaderboard_events(event)
            
            # Update game if playing
            if self.current_screen == "game":
                self.snake_game.update()
            
            # Draw current screen
            if self.current_screen == "onboarding":
                self.draw_onboarding_screen()
            elif self.current_screen == "game":
                self.draw_game_screen()
            elif self.current_screen == "leaderboard":
                self.draw_leaderboard_screen()
            
            # Update display and control frame rate
            pygame.display.update()
            fps.tick(snake_speed)
        
        # Clean up
        pygame.quit()
        sys.exit()

# Main execution
if __name__ == "__main__":
    # Create and run the expo game system
    expo_system = ExpoGameSystem()
    expo_system.run()