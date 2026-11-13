

# USD per 1M tokens. Source: OpenAI model pages, checked 2026-11-11
PRICES = {
    "gpt-5.4-mini": {"input": 0.75, "output": 4.50},
    "gpt-4o-mini":  {"input": 0.15, "output": 0.60},
}

def cost_breakdown(model: str, usage) -> dict:
    if model not in PRICES:
        raise ValueError(f"No price configured for model '{model}'")
    p = PRICES[model]
    input_cost = usage.input_tokens * p["input"] / 1_000_000
    output_cost = usage.output_tokens * p["output"] / 1_000_000
    
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "cost": input_cost + output_cost,
    }

def calculate_cost(model:str,usage)->float:
    # Total cost in USD. Used for the database and monitoring
    return cost_breakdown(model, usage)["cost"]