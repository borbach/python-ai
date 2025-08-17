from pydantic_ai import Agent

agent = Agent(  
    'google-gla:gemini-1.5-flash',
    system_prompt='Be angry and impatient'
)
 
question = ""

while question != "end":
    question = input("what would you like to know:  ")
    result = agent.run_sync(question)  
    print(result.output)


