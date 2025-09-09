#!/usr/bin/env python3
"""
Supabase Configuration Validation Script

This script validates Supabase project connectivity and configuration
for all NutriFit microservices.
"""

import os
import asyncio
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncpg
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/environments/supabase.env.template')

@dataclass
class SupabaseProject:
    """Supabase project configuration."""
    name: str
    url: str
    anon_key: Optional[str]
    service_key: str
    db_url: Optional[str] = None  # For PostgreSQL direct connections
    connection_type: str = "client"  # "client" or "direct"

class SupabaseValidator:
    """Validates Supabase configuration and connectivity."""
    
    def __init__(self):
        self.projects = self._load_projects()
        self.results: List[Dict] = []
    
    def _load_projects(self) -> List[SupabaseProject]:
        """Load Supabase projects from environment variables."""
        projects = [
            SupabaseProject(
                name="user-management",
                url=os.getenv("SUPABASE_USER_MANAGEMENT_URL", ""),
                anon_key=os.getenv("SUPABASE_USER_MANAGEMENT_ANON_KEY", ""),
                service_key=os.getenv("SUPABASE_USER_MANAGEMENT_SERVICE_KEY", ""),
                connection_type="client"
            ),
            SupabaseProject(
                name="calorie-balance",
                url=os.getenv("SUPABASE_CALORIE_BALANCE_URL", ""),
                service_key=os.getenv("SUPABASE_CALORIE_BALANCE_SERVICE_KEY", ""),
                db_url=os.getenv("SUPABASE_CALORIE_BALANCE_DB_URL", ""),
                connection_type="direct"
            ),
            SupabaseProject(
                name="meal-tracking",
                url=os.getenv("SUPABASE_MEAL_TRACKING_URL", ""),
                anon_key=os.getenv("SUPABASE_MEAL_TRACKING_ANON_KEY", ""),
                service_key=os.getenv("SUPABASE_MEAL_TRACKING_SERVICE_KEY", ""),
                connection_type="client"
            ),
            SupabaseProject(
                name="health-monitor",
                url=os.getenv("SUPABASE_HEALTH_MONITOR_URL", ""),
                anon_key=os.getenv("SUPABASE_HEALTH_MONITOR_ANON_KEY", ""),
                service_key=os.getenv("SUPABASE_HEALTH_MONITOR_SERVICE_KEY", ""),
                connection_type="client"
            ),
            SupabaseProject(
                name="notifications",
                url=os.getenv("SUPABASE_NOTIFICATIONS_URL", ""),
                anon_key=os.getenv("SUPABASE_NOTIFICATIONS_ANON_KEY", ""),
                service_key=os.getenv("SUPABASE_NOTIFICATIONS_SERVICE_KEY", ""),
                connection_type="client"
            ),
            SupabaseProject(
                name="ai-coach",
                url=os.getenv("SUPABASE_AI_COACH_URL", ""),
                service_key=os.getenv("SUPABASE_AI_COACH_SERVICE_KEY", ""),
                db_url=os.getenv("SUPABASE_AI_COACH_DB_URL", ""),
                connection_type="direct"
            ),
        ]
        return projects
    
    async def validate_all(self) -> bool:
        """Validate all Supabase projects."""
        print("🔍 Validating Supabase Configuration...\n")
        
        all_valid = True
        
        for project in self.projects:
            result = await self._validate_project(project)
            self.results.append(result)
            all_valid &= result["valid"]
        
        self._print_summary()
        return all_valid
    
    async def _validate_project(self, project: SupabaseProject) -> Dict:
        """Validate a single Supabase project."""
        print(f"📡 Validating {project.name}...")
        
        result = {
            "name": project.name,
            "valid": False,
            "checks": {},
            "errors": []
        }
        
        # Check configuration completeness
        config_valid = self._validate_config(project, result)
        
        if not config_valid:
            print(f"❌ {project.name}: Configuration incomplete")
            return result
        
        # Test connectivity
        try:
            if project.connection_type == "client":
                await self._test_supabase_client(project, result)
            else:
                await self._test_postgresql_direct(project, result)
            
            result["valid"] = all(result["checks"].values())
            
            if result["valid"]:
                print(f"✅ {project.name}: All checks passed")
            else:
                print(f"❌ {project.name}: Some checks failed")
                
        except Exception as e:
            result["errors"].append(f"Connection test failed: {str(e)}")
            print(f"❌ {project.name}: Connection failed - {str(e)}")
        
        return result
    
    def _validate_config(self, project: SupabaseProject, result: Dict) -> bool:
        """Validate project configuration completeness."""
        checks = []
        
        # URL check
        if project.url and project.url.startswith("https://"):
            result["checks"]["url"] = True
        else:
            result["checks"]["url"] = False
            result["errors"].append("Missing or invalid Supabase URL")
        
        # Service key check
        if project.service_key and len(project.service_key) > 50:
            result["checks"]["service_key"] = True
        else:
            result["checks"]["service_key"] = False
            result["errors"].append("Missing or invalid service key")
        
        # Connection type specific checks
        if project.connection_type == "client":
            if project.anon_key and len(project.anon_key) > 50:
                result["checks"]["anon_key"] = True
            else:
                result["checks"]["anon_key"] = False
                result["errors"].append("Missing or invalid anon key")
        else:
            if project.db_url and project.db_url.startswith("postgresql://"):
                result["checks"]["db_url"] = True
            else:
                result["checks"]["db_url"] = False
                result["errors"].append("Missing or invalid PostgreSQL URL")
        
        return all(result["checks"].values())
    
    async def _test_supabase_client(self, project: SupabaseProject, result: Dict):
        """Test Supabase client connection."""
        async with httpx.AsyncClient() as client:
            # Test REST API endpoint
            headers = {
                "apikey": project.service_key,
                "Authorization": f"Bearer {project.service_key}",
                "Content-Type": "application/json"
            }
            
            try:
                response = await client.get(
                    f"{project.url}/rest/v1/",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code in [200, 404]:  # 404 is ok for base endpoint
                    result["checks"]["rest_api"] = True
                else:
                    result["checks"]["rest_api"] = False
                    result["errors"].append(f"REST API returned {response.status_code}")
                    
            except Exception as e:
                result["checks"]["rest_api"] = False
                result["errors"].append(f"REST API test failed: {str(e)}")
    
    async def _test_postgresql_direct(self, project: SupabaseProject, result: Dict):
        """Test PostgreSQL direct connection."""
        try:
            conn = await asyncpg.connect(project.db_url)
            
            # Test basic query
            await conn.execute("SELECT 1")
            result["checks"]["postgresql_connection"] = True
            
            # Test database info
            version = await conn.fetchval("SELECT version()")
            result["checks"]["postgresql_version"] = bool(version)
            
            await conn.close()
            
        except Exception as e:
            result["checks"]["postgresql_connection"] = False
            result["errors"].append(f"PostgreSQL connection failed: {str(e)}")
    
    def _print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        
        for result in self.results:
            status = "✅ PASS" if result["valid"] else "❌ FAIL"
            print(f"{result['name']:20} {status}")
            
            if result["errors"]:
                for error in result["errors"]:
                    print(f"  • {error}")
        
        print("\n" + "="*60)
        
        valid_count = sum(1 for r in self.results if r["valid"])
        total_count = len(self.results)
        
        if valid_count == total_count:
            print("🎉 All Supabase projects configured correctly!")
        else:
            print(f"⚠️  {total_count - valid_count}/{total_count} projects need attention")
        
        print("="*60)

async def main():
    """Main validation function."""
    print("🚀 NutriFit Supabase Configuration Validator")
    print("="*60)
    
    validator = SupabaseValidator()
    
    try:
        is_valid = await validator.validate_all()
        
        if is_valid:
            print("\n✅ Ready to proceed with microservices implementation!")
            sys.exit(0)
        else:
            print("\n❌ Please fix configuration issues before proceeding.")
            print("\n📖 See config/supabase/SETUP_GUIDE.md for help")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Validation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
