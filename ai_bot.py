import time 

def ai_assistant():

    print("🤖 Buddy: Hello! I am Buddy, your simple AI assistant.")
    print("🤖 Buddy: Ask me a question, or type 'exit' to leave.")

    while True:
        user_input = input("\nYou: ").lower()
       
        #check if the user wants to exit
        if 'exit' in user_input or 'bye' in user_input:
                print("🤖 Buddy: Goodbye! Have a great day!")
                break

                # AI Logic: Keyword Matching
        elif "hello" in user_input or "hi" in user_input:
            print("🤖 Buddy: Hello there! How can I help you today?")
            
        elif "your name" in user_input:
            print("🤖 Buddy: My name is Buddy. I'm a simple Python AI!")
            
        elif "how are you" in user_input:
            print("🤖 Buddy: I don't have feelings, but my code is running perfectly! Thanks for asking.")
            
        elif "time" in user_input:
            current_time = time.strftime("%H:%M:%S")
            print(f"🤖 Buddy: The current time is {current_time}.")
            
        elif "weather" in user_input:
            print("🤖 Buddy: I cannot check live weather right now, but I hope it's sunny where you are!")
            
        # Default response if the AI doesn't understand
        else:
            print(f"🤖 Buddy: You said '{user_input}'. I'm still learning, so I can't answer that yet.")



# RUN THE ai_assistant function if this script is executed directly
if __name__ == "__main__":
    ai_assistant()
    