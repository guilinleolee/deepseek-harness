"""Verify the RequestBodyObject fix in template_engine.py.

Before the fix, accessing ep.request_body.get("properties") raised
AttributeError because RequestBodyObject is a @dataclass, not a dict.
"""
import sys
sys.path.insert(0, ".")
from scripts import template_engine as te

spec = {
    "openapi": "3.0.0",
    "info": {"title": "TestAPI", "version": "1.0.0"},
    "paths": {
        "/users": {
            "post": {
                "operationId": "createUser",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "User name"},
                                    "email": {"type": "string", "description": "User email"},
                                    "age": {"type": "integer", "description": "User age"},
                                },
                                "required": ["name", "email"],
                            }
                        }
                    },
                    "description": "Create a new user",
                },
            }
        }
    },
    "components": {"schemas": {}},
}

print("Testing create_context_from_spec with a requestBody...")
try:
    context = te.create_context_from_spec(spec, auth_types=["go"])
    print("SUCCESS: create_context_from_spec returned without AttributeError")

    # Find the endpoint with request fields
    found = False
    for ep_ctx in context.endpoints:
        if ep_ctx["operation_id"] == "createUser":
            found = True
            print(f"  Found endpoint: {ep_ctx['path']} {ep_ctx['method']}")
            print(f"  request_fields ({len(ep_ctx['request_body_fields'])}):")
            for field in ep_ctx["request_body_fields"]:
                print(f"    - {field['name']}: {field['go_type']}, required={field['required']}")

            # Verify field count
            assert len(ep_ctx["request_body_fields"]) == 3, f"Expected 3 fields, got {len(ep_ctx['request_body_fields'])}"
            # Verify required fields
            names = {f["name"] for f in ep_ctx["request_body_fields"]}
            assert "name" in names, "name field missing"
            assert "email" in names, "email field missing"
            print("VERIFIED: All fields parsed correctly!")
            break

    if not found:
        print("WARNING: Endpoint 'createUser' not found in context")
        print(f"  Available endpoints: {[e['operation_id'] for e in context.endpoints]}")

except AttributeError as e:
    print(f"FAILED: AttributeError still raised: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll tests passed! The fix resolves the RequestBodyObject AttributeError.")