import sys
import os

# Add the root directory to the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)

try:
    from mangum import Mangum
    from main import app as fastapi_app
    
    # Create the Mangum handler for AWS Lambda/Netlify Functions
    handler = Mangum(fastapi_app, lifespan="off")
    
except ImportError as e:
    # Fallback handler if imports fail
    def handler(event, context):
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': f'{{"error": "Import error: {str(e)}"}}'
        }