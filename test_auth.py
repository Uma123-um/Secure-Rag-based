from auth import create_token, verify_token

token = create_token(
    "Uma",
    "HR"
)

print("Generated Token:\n")
print(token)

print("\nDecoded Payload:\n")

payload = verify_token(token)

print(payload)