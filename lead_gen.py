import random
import json
import os
from faker import Faker
from database import init_db, add_leads

# Set a seed for reproducibility
# Faker.seed(42)
fake = Faker()

CONFIG_FILE = "config.json"

def load_config():
    """Load industry/role mappings from JSON config."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file {CONFIG_FILE} not found.")
    
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def generate_leads(count=200,seed=None):
    industries_map = load_config()
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    # LOAD CONFIG DYNAMICALLY
    
    
    leads = []
    print(f"Generating {count} leads using configurable rules...")
    
    for _ in range(count):
        # Pick random industry from the config keys
        industry = random.choice(list(industries_map.keys()))
        # Pick random role from that industry's list
        role = random.choice(industries_map[industry])
        
        company = fake.company()
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Ensure syntactic validity
        clean_company = company.replace(' ', '').replace(',', '').replace('.', '').lower()
        email = f"{first_name.lower()}.{last_name.lower()}@{clean_company}.com"
        
        lead = {
            "full_name": f"{first_name} {last_name}",
            "company_name": company,
            "role": role,
            "industry": industry,
            "website": f"https://www.{clean_company}.com",
            "email": email,
            "linkedin_url": f"https://www.linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
            "country": fake.country()
        }
        leads.append(lead)
        
    return leads

if __name__ == "__main__":
    init_db()
    generated_data = generate_leads(count=200, seed=42)
    add_leads(generated_data)
# import random
# from faker import Faker
# from database import init_db, add_leads

# # Set a seed for reproducibility [cite: 37]
# Faker.seed(42)
# fake = Faker()

# INDUSTRIES = {
#     "Technology": ["Software Engineer", "CTO", "Product Manager", "DevOps Engineer"],
#     "Healthcare": ["Medical Director", "Operations Manager", "Supply Chain Lead", "Procurement Head"],
#     "Finance": ["Financial Analyst", "VP of Finance", "Investment Manager", "Risk Officer"],
#     "Retail": ["Supply Chain Manager", "Marketing Director", "Store Manager", "Buyer"],
#     "Manufacturing": ["Plant Manager", "Production Supervisor", "Quality Control Lead", "Operations Director"]
# }

# def generate_leads(count=200):
#     leads = []
#     print(f"Generating {count} leads...")
    
#     for _ in range(count):
#         industry = random.choice(list(INDUSTRIES.keys()))
#         role = random.choice(INDUSTRIES[industry])
#         company = fake.company()
#         first_name = fake.first_name()
#         last_name = fake.last_name()
        
#         # Ensure syntactic validity for emails and URLs [cite: 30, 31, 32]
#         email = f"{first_name.lower()}.{last_name.lower()}@{company.replace(' ', '').replace(',', '').lower()}.com"
        
#         lead = {
#             "full_name": f"{first_name} {last_name}",
#             "company_name": company,
#             "role": role,
#             "industry": industry,
#             "website": f"https://www.{company.replace(' ', '').replace(',', '').lower()}.com",
#             "email": email,
#             "linkedin_url": f"https://www.linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
#             "country": fake.country()
#         }
#         leads.append(lead)
        
#     return leads

# if __name__ == "__main__":
#     # Initialize DB if not exists
#     init_db()
    
#     # Generate and save
#     generated_data = generate_leads(210) # Generating slightly more than 200 
#     add_leads(generated_data)