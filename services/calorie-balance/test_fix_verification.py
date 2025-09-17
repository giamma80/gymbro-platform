#!/usr/bin/env python3
"""
Quick test to verify MetabolicProfile fix
"""

import sys
import os
sys.path.append('/Users/giamma/workspace/gymbro-platform/services/calorie-balance')

from app.domain.entities import MetabolicProfile
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

def test_metabolic_profile_fix():
    """Test that MetabolicProfile works with all required fields."""
    print("🧪 Testing MetabolicProfile entity fix...")
    
    # Test data matching the 009_test_data_preparation.sql schema
    profile_data = {
        'id': uuid4(),
        'created_at': datetime.now(),
        'updated_at': datetime.now(),
        'user_id': uuid4(),
        'bmr_calories': Decimal('1650'),
        'tdee_calories': Decimal('2100'),
        'rmr_calories': Decimal('1720'),
        'calculation_method': 'harris_benedict_revised',
        'accuracy_score': Decimal('0.85'),
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
    
    try:
        # This should work now - previously would fail with AttributeError
        profile = MetabolicProfile(**profile_data)
        print("✅ SUCCESS: MetabolicProfile created successfully!")
        
        # Test the fields that were previously causing errors
        print(f"   📊 RMR Calories: {profile.rmr_calories}")
        print(f"   🎯 Accuracy Score: {profile.accuracy_score}")
        print(f"   🏃 Activity Level: {profile.activity_level}")
        print(f"   🤖 AI Adjusted: {profile.ai_adjusted}")
        print(f"   ⚡ Adjustment Factor: {profile.adjustment_factor}")
        print(f"   🧠 Learning Iterations: {profile.learning_iterations}")
        print(f"   ⏰ Calculated At: {profile.calculated_at}")
        print(f"   🟢 Is Active: {profile.is_active}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graphql_types_import():
    """Test that GraphQL types import correctly."""
    print("\n🔌 Testing GraphQL types import...")
    
    try:
        from app.graphql.extended_types import MetabolicProfileType, CalorieEventType
        print("✅ SUCCESS: GraphQL types imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 METABOLIC PROFILE ENTITY FIX VERIFICATION")
    print("=" * 60)
    
    success_count = 0
    total_tests = 2
    
    if test_metabolic_profile_fix():
        success_count += 1
        
    if test_graphql_types_import():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 RESULT: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED! Ready for comprehensive testing.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above.")
        sys.exit(1)