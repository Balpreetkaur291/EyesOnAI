from vapi import Vapi

client = Vapi(token="vapi_api_key")  # Replace with your actual API key

def make_outbound_call(assistant_id: str, phone_number: str):
    try:
        call = client.calls.create(
            assistant_id=assistant_id,
            phone_number_id="VAPI_PHONE_ID", 
            customer={
                "number": phone_number, 
            },
        )
        
        print(f"Outbound call initiated: {call.id}")
        return call
    except Exception as error:
        print(f"Error making outbound call: {error}")
        raise error

