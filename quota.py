import google.generativeai as generativeai




def get_gemini_usage_and_limit(project_id, location):
    """Retrieves Gemini usage and limit information.

    Args:
        project_id: Your Google Cloud project ID.
        location: The region or location (e.g., "us-central1").

    Returns:
      A dictionary containing request, token, and model usage (if available) information or None if an error occurs.

    """

    metrics = [
        "GEN_AI_REQUESTS",  # Number of requests
        "GEN_AI_TOKENS", # Number of tokens
        # Add other relevant metrics if available
    ]

    usage_and_limit = {}

    for metric in metrics:
      quota_info = get_gemini_quota(project_id, location, metric)

      if quota_info:
        usage_and_limit[metric] = {
            "limit": quota_info['limit'],
            "usage": quota_info['usage'],
        }
      else:
        print(f"Could not retrieve quota information for metric: {metric}")

    return usage_and_limit



# Example usage:
project_id = "your-project-id"  # Replace with your project ID
location = "us-central1"  # Replace with the location

usage_and_limit = get_gemini_usage_and_limit(project_id, location)

if usage_and_limit:
    print("Gemini Usage and Limits:")
    for metric, info in usage_and_limit.items():
        print(f"  {metric}:")
        print(f"    Limit: {info['limit']}")
        print(f"    Usage: {info['usage']}")
        balance = info['limit'] - info['usage']
        print(f"    Balance: {balance}")

else:
    print("Failed to retrieve Gemini usage and limit information.")