import speech
import aimodels

system_prompt = """You are a helpful AI tutor, Help the user learn english by teaching each words,
                 where explanation section to talk the the user give these outputs as if you are speaking irl,
                 and always use under 20 words"""

conversation = []

while True:
    user_inp = input("You: ")

    conversation.append({
        "role": "user",
        "content": [{"type": "text", "text": user_inp}]
    })

    reply = aimodels.claude3_tuff(system_prompt, conversation)

    print(reply)
    print(reply['explanation'])

    # print("Assistant:", reply["raw_text"]) 
    # speech.speak(reply)

    # If you want to maintain conversation:
    conversation.append({
        "role": "assistant",
        "content": [{"type": "text", "text": reply}]
    })

    A:\Amartya\College Stuff\hackathon\aimodels.py