"""
main.py - FastAPI Application Entrypoint

Exposes the CX Agent via REST API:
- POST /agentic-cx: Submit customer message and receive agent decision
- GET /health: Health check endpoint
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from agent import CXAgent

# Initialize FastAPI app
app = FastAPI(
    title="Agentic CX PoC",
    description="Autonomous AI agent for contact center customer experience",
    version="1.0.0",
)

# Add CORS middleware to allow requests from the web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo purposes
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Initialize the CX Agent
# Uses 'data' directory for mock data (relative to where main.py is run from)
data_dir = os.path.join(os.path.dirname(__file__), "data")
agent = CXAgent(data_dir=data_dir)


# ==================== API MODELS ====================

class CustomerMessage(BaseModel):
    """Request model for customer message submission."""
    customer_id: str
    message: str


class AgentResponse(BaseModel):
    """Response model from the agent."""
    intent: str
    goal: str
    decision: str
    decision_type: str
    actions_taken: list
    status: str
    confidence: float
    explanation: str
    escalation_ticket: Optional[dict] = None
    appointment_details: Optional[dict] = None
    confirmation_sent: Optional[dict] = None


# ==================== ENDPOINTS ====================

@app.post("/agentic-cx", response_model=AgentResponse)
async def process_customer_request(request: CustomerMessage) -> AgentResponse:
    """
    Main endpoint: Submit a customer message to the CX Agent.

    The agent will:
    1. Detect the customer's intent
    2. Assess eligibility and available data
    3. Make an autonomous decision
    4. Execute the appropriate action
    5. Return a structured response

    Args:
        customer_id: Unique identifier for the customer
        message: Natural language message from the customer

    Returns:
        AgentResponse with intent, decision, actions, and status

    Example:
        {
            "customer_id": "123",
            "message": "I missed my appointment yesterday, can I rebook it?"
        }
    """
    try:
        # Validate inputs
        if not request.customer_id or not request.customer_id.strip():
            raise HTTPException(status_code=400, detail="customer_id is required")

        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="message is required")

        # Process the customer message through the agent
        result = agent.process_customer_message(
            customer_id=request.customer_id,
            message=request.message,
        )

        return AgentResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "Agentic CX PoC",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Agentic AI CX PoC",
        "description": "Autonomous agent for contact center operations",
        "endpoints": {
            "POST /agentic-cx": "Submit customer message for processing",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation (Swagger)",
        },
        "example_request": {
            "customer_id": "123",
            "message": "I missed my appointment yesterday, can I rebook it?"
        }
    }


# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    print("=" * 60)
    print("Agentic CX PoC - Starting up")
    print("=" * 60)
    print(f"Data directory: {data_dir}")
    print("API available at: http://localhost:8000")
    print("Documentation: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
