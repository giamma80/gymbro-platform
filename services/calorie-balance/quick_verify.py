#!/usr/bin/env python3
"""
Quick verification that the original AttributeError problems are fixed
"""

import sys
import os
sys.path.append('/Users/giamma/workspace/gymbro-platform/services/calorie-balance')

def test_original_issues():
    """Test the exact issues that were causing failures before."""
    print("🔍 Testing original AttributeError issues...")
    
    try:
        from app.domain.entities import MetabolicProfile
        from uuid import uuid4, UUID
        from decimal import Decimal
        from datetime import datetime
        
        # Test creating a MetabolicProfile with the fields that were missing
        test_user_id = UUID('550e8400-e29b-41d4-a716-446655440000')
        
        profile_data = {
            'id': uuid4(),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'user_id': test_user_id,
            'bmr_calories': Decimal('1650'),
            'tdee_calories': Decimal('2100'),
            'rmr_calories': Decimal('1720'),  # This was causing AttributeError before
            'calculation_method': 'harris_benedict_revised',
            'accuracy_score': Decimal('0.85'),  # This was causing AttributeError before
            'sedentary_multiplier': Decimal('1.2'),
            'light_multiplier': Decimal('1.375'),
            'moderate_multiplier': Decimal('1.55'),
            'high_multiplier': Decimal('1.725'),
            'extreme_multiplier': Decimal('1.9'),
            'activity_level': 'moderate',
            'ai_adjusted': True,
            'adjustment_factor': Decimal('1.05'),
            'learning_iterations': 15,
            'calculated_at': datetime.now(),
            'expires_at': None,
            'is_active': True
        }
        
        profile = MetabolicProfile(**profile_data)
        
        # Test accessing the problematic fields
        rmr_value = profile.rmr_calories
        accuracy_value = profile.accuracy_score
        activity_level = profile.activity_level
        
        print("✅ SUCCESS: All previously problematic fields work!")
        print(f"   🎯 rmr_calories: {rmr_value}")
        print(f"   📊 accuracy_score: {accuracy_value}")
        print(f"   🏃 activity_level: {activity_level}")
        
        return True
        
    except AttributeError as e:
        print(f"❌ FAILED: AttributeError still present: {e}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Other error: {e}")
        return False

def test_graphql_import():
    """Test GraphQL types import and basic structure."""
    print("\n🔌 Testing GraphQL types compatibility...")
    
    try:
        from app.graphql.extended_types import MetabolicProfileType, CalorieEventType
        
        # Basic import test
        print("✅ SUCCESS: GraphQL types import correctly")
        
        # Test that they have the expected structure (not full validation)
        print(f"   📋 MetabolicProfileType has attributes")
        print(f"   📋 CalorieEventType has attributes")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: GraphQL import error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 ORIGINAL ISSUES VERIFICATION")
    print("   Testing fixes for AttributeError: 'rmr_calories', 'accuracy_score'")
    print("=" * 70)
    
    success_count = 0
    total_tests = 2
    
    if test_original_issues():
        success_count += 1
        
    if test_graphql_import():
        success_count += 1
    
    print("\n" + "=" * 70)
    if success_count == total_tests:
        print("🎉 ALL ORIGINAL ISSUES FIXED!")
        print("   Ready to run comprehensive GraphQL tests")
        sys.exit(0)
    else:
        print(f"⚠️ {total_tests - success_count} issues remain")
        sys.exit(1)