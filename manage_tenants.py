# manage_tenants.py
import asyncio
import argparse
# Import your custom session managers
from src.database.session import transaction_scope, get_repository_db 
from src.services.system.tenant_service import provision_tenant

async def async_main():
    # 1. Set up CLI Argument Parser
    parser = argparse.ArgumentParser(description="Async CRM Tenant Management CLI")
    parser.add_argument("--company_name", required=True, help="Company/Tenant Name")
    parser.add_argument("--company_tin", required=False, help="Company/Tenant TIN")

    parser.add_argument("--admin-firstname", required=True, help="Admin firstname")
    parser.add_argument("--admin-login", required=True, help="Admin login")
    parser.add_argument("--admin-password", required=False, help="Admin password")
    args = parser.parse_args()

    try:
        # 2. Enter your custom transaction scope (Handles Session, Commit, and Rollback automatically!)
        async with transaction_scope():
            
            # 3. Fetch the active session from your ContextVar
            db = get_repository_db()
            
            print(f"⏳ Provisioning tenant '{args.company_name}'...")
            result = await provision_tenant(
                db=db,
                company_name=args.company_name,    
                company_tin=args.company_tin,      
                admin_login=args.admin_login,
                admin_firstname=args.admin_firstname,
                admin_password=args.admin_password,
            )
            
            print(f"✅ Success! Tenant '{result['tenant'].name}' created with ID: {result['tenant'].id}")
            print(f"Admin login: '{result['login']}', password: '{result['password']}'")
            print(f"🔧 Automated transaction wrapper is committing your changes safely...")

    except Exception as e:
        print(f"❌ Critical Error: Tenant creation failed.")
        print(f"Details: {e}")
        print(f"↩️ Transaction was rolled back automatically by transaction_scope.")

if __name__ == "__main__":
    asyncio.run(async_main())