from kb.models import KnowledgeBaseEntry
from request.models import Request, Customer
from supervisor.models import SupervisorResponse
from agent.models import AIResponse

def get_kb_answer(question: str):
    """Check if KB has an answer."""
    entry = KnowledgeBaseEntry.objects.filter(question__icontains=question).first()
    return entry.answer if entry else None

def handle_incoming_call(customer: Customer, question: str, description=""):
    """AI receives a call/question."""
    answer = get_kb_answer(question)
    if answer:
        # AI knows the answer
        request = Request.objects.create(customer=customer, question=question, description=description, status="RESOLVED")
        AIResponse.objects.create(request=request, answer_text=answer)
        print(f"AI → {customer.name}: {answer}")
        return request

    # AI doesn't know: create pending request
    request = Request.objects.create(customer=customer, question=question, description=description, status="PENDING")
    print(f"AI → {customer.name}: Let me check with my supervisor and get back to you.")
    print(f"Supervisor Alert: Need help answering '{question}' from {customer.name}")
    return request

def follow_up_with_customer(request: Request):
    """Send response to customer after supervisor answers."""
    if hasattr(request, 'supervisor_response'):
        answer = request.supervisor_response.answer
        print(f"AI → {request.customer.name}: {answer}")
        # Save answer to knowledge base
        KnowledgeBaseEntry.objects.create(
            question=request.question,
            answer=answer,
            source_request=request
        )
        request.status = "RESOLVED"
        request.save()
