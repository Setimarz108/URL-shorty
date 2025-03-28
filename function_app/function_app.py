import azure.functions as func
import logging
import uuid
import validators
import os
from datetime import datetime
from azure.data.tables import TableServiceClient, UpdateMode
from azure.core.exceptions import ResourceExistsError

app = func.FunctionApp()

# Helper functions for Table Storage operations
def get_table_client():
    """Get or create the URL shortener table"""
    try:
        # Get connection string from app settings
        connection_string = os.environ["AzureWebJobsStorage"]
        
        # Create table service client
        table_service = TableServiceClient.from_connection_string(connection_string)
        
        # Create table if it doesn't exist
        table_name = "urlshortener"
        try:
            table_client = table_service.create_table_if_not_exists(table_name)
        except ResourceExistsError:
            table_client = table_service.get_table_client(table_name)
            
        return table_client
    except Exception as e:
        logging.error(f"Error connecting to Table Storage: {str(e)}")
        raise

def save_url(short_code, original_url):
    """Save URL mapping to Table Storage"""
    try:
        table_client = get_table_client()
        
        # Create entity
        entity = {
            "PartitionKey": "urls",
            "RowKey": short_code,
            "OriginalUrl": original_url,
            "CreatedAt": datetime.now().isoformat(),
            "Clicks": 0
        }
        
        # Add entity to table
        table_client.create_entity(entity)
        
        logging.info(f"Saved URL mapping: {short_code} -> {original_url}")
        return True
    except Exception as e:
        logging.error(f"Error saving URL: {str(e)}")
        return False

def get_url(short_code):
    """Get original URL from Table Storage"""
    try:
        table_client = get_table_client()
        
        # Query for entity
        entity = table_client.get_entity("urls", short_code)
        
        # Update click count
        entity["Clicks"] += 1
        table_client.update_entity(entity, mode=UpdateMode.REPLACE)
        
        return entity["OriginalUrl"]
    except Exception as e:
        logging.error(f"Error retrieving URL: {str(e)}")
        return None

@app.function_name("create_short_url")
@app.route(route="create_short_url", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST", "OPTIONS"])
def create_short_url(req: func.HttpRequest) -> func.HttpResponse:
    """Create a short URL"""
    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        })
    
    try:
        # Get URL from request
        req_body = req.get_json()
        url = req_body.get('url', '')
        
        # Validate URL
        if not url:
            return func.HttpResponse("URL is required", status_code=400, 
                                    headers={"Access-Control-Allow-Origin": "*"})
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        if not validators.url(url):
            return func.HttpResponse("Invalid URL format", status_code=400,
                                    headers={"Access-Control-Allow-Origin": "*"})
        
        # Generate unique ID
        short_code = str(uuid.uuid4())[:6]
        
        # Store URL
        if save_url(short_code, url):
            # Build short URL (use actual function app URL in production)
            function_app_url = os.environ.get("FUNCTION_APP_URL", "http://localhost:7071")
            short_url = f"{function_app_url}/api/r/{short_code}"
            
            return func.HttpResponse(
                short_url,
                status_code=200,
                headers={"Access-Control-Allow-Origin": "*"}
            )
        else:
            return func.HttpResponse(
                "Error saving URL",
                status_code=500,
                headers={"Access-Control-Allow-Origin": "*"}
            )
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            f"An error occurred",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )

@app.function_name("redirect")
@app.route(route="r/{code}", auth_level=func.AuthLevel.ANONYMOUS)
def redirect(req: func.HttpRequest) -> func.HttpResponse:
    """Redirect short URL to original URL"""
    try:
        code = req.route_params.get('code')
        original_url = get_url(code)
        
        if original_url:
            return func.HttpResponse(
                status_code=302,
                headers={
                    "Location": original_url,
                    "Access-Control-Allow-Origin": "*"
                }
            )
        else:
            return func.HttpResponse(
                "URL not found",
                status_code=404,
                headers={"Access-Control-Allow-Origin": "*"}
            )
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(
            "An error occurred",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )