from supabase import Client, create_client

from backend.core.config import(
    SUPABASE_URL,
    SUPABASE_KEY,

)

if not SUPABASE_URL or SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set in the .env file."
    )
supabase: Client = create_client( #reusable client
    SUPABASE_URL,
    SUPABASE_KEY,
)

