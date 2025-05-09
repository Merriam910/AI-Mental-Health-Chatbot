# chatbot/chatbot_core.py

from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration

# Load model and tokenizer once
tokenizer = BlenderbotTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = BlenderbotForConditionalGeneration.from_pretrained("facebook/blenderbot-400M-distill")

def chat_with_blenderbot(user_input):
    inputs = tokenizer([user_input], return_tensors="pt")
    reply_ids = model.generate(**inputs)
    response = tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
    return response
