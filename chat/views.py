from django.shortcuts import render
from django.http import JsonResponse
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model once when server starts
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

# Home page
def index(request):
    return render(request, 'chat/home.html')

# AI chat response
def ask_ai(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        try:
            # Encode the user input
            input_ids = tokenizer.encode(user_message + tokenizer.eos_token, return_tensors='pt')
            
            # Generate a response
            chat_history_ids = model.generate(
                input_ids,
                max_length=1000,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True,       # Important! enables randomness
                top_k=50,             # only sample from top 50 predictions
                top_p=0.95,           # nucleus sampling
                temperature=0.8 
            )
            
            # Decode the output
            answer = tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
            
            return JsonResponse({'answer': answer})
        except Exception as e:
            return JsonResponse({'answer': f"Error: {str(e)}"})
    return JsonResponse({'answer': 'Invalid request'})
