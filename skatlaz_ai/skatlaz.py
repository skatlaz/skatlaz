from skatlaz_prompt import SkatlazAI

# Initialize
skatlaz = SkatlazAI()

# Process prompt
print("🤖 Skatlaz AI iniciado\n")
prompt = input("🤖 ASK FOR SKATLAZ: ")
response = skatlaz.process_prompt(prompt)
print(response)

# Interactive mode
skatlaz.interactive_mode()
