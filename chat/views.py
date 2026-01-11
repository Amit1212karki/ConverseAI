from django.shortcuts import render
from django.http import JsonResponse
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model once when server starts
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

chat_sessions = {}

def index(request):
    return render(request, 'chat/home.html')

def ask_ai(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        session_id = request.session.session_key

        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        # Load previous chat
        if session_id not in chat_sessions:
            chat_sessions[session_id] = None

        try:
            # Encode new message
            new_input_ids = tokenizer.encode(
                user_message + tokenizer.eos_token,
                return_tensors='pt'
            )

            # Combine with history
            if chat_sessions[session_id] is not None:
                input_ids = torch.cat(
                    [chat_sessions[session_id], new_input_ids],
                    dim=-1
                )
            else:
                input_ids = new_input_ids

            # Generate response
            chat_history_ids = model.generate(
                input_ids,
                max_length=1000,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.8,
                pad_token_id=tokenizer.eos_token_id
            )

            # Save history
            chat_sessions[session_id] = chat_history_ids

            # Decode only new text
            response = tokenizer.decode(
                chat_history_ids[:, input_ids.shape[-1]:][0],
                skip_special_tokens=True
            )

            return JsonResponse({'answer': response})

        except Exception as e:
            return JsonResponse({'answer': f"Error: {str(e)}"})

    return JsonResponse({'answer': 'Invalid request'})
