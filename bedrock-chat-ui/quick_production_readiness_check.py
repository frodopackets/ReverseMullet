#!/usr/bin/env python3
"""
Quick production readiness check focusing on cost accuracy
"""

import sys
import os
import asyncio
import json

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def quick_readiness_check():
    print("🚀 Quick Production Readiness Check")
    print("=" * 40)
    
    # Check if cost validation report exists
    try:
        with open('cost_validation_report.json', 'r') as f:
            cost_report = json.load(f)
        
        cost_score = cost_report.get('overall_score', 0)
        extraction_rate = cost_report.get('extraction_rate', 0)
        accuracy_rate = cost_report.get('accuracy_rate', 0)
        
        print(f"📊 Cost Validation Results:")
        print(f"   Overall Score: {cost_score:.1f}/100")
        print(f"   Extraction Rate: {extraction_rate:.1f}%")
        print(f"   Accuracy Rate: {accuracy_rate:.1f}%")
        
        # Production readiness criteria
        criteria = [
            ("Cost Extraction", extraction_rate >= 90, f"AI can extract costs from responses ({extraction_rate:.1f}%)"),
            ("Cost Accuracy", accuracy_rate >= 70, f"AI provides reasonably accurate estimates ({accuracy_rate:.1f}%)"),
            ("Overall Cost Score", cost_score >= 70, f"Overall cost validation meets standards ({cost_score:.1f}/100)")
        ]
        
        passed_criteria = sum(1 for _, passed, _ in criteria if passed)
        total_criteria = len(criteria)
        readiness_score = (passed_criteria / total_criteria) * 100
        
        print(f"\n🎯 Production Readiness Assessment:")
        for criterion, passed, description in criteria:
            status_icon = "✅" if passed else "❌"
            print(f"   {status_icon} {criterion}: {description}")
        
        print(f"\n🏆 Production Readiness Score: {readiness_score:.1f}%")
        
        if readiness_score >= 90:
            print("   🎉 EXCELLENT - Ready for production!")
        elif readiness_score >= 80:
            print("   ✅ GOOD - Meets production standards")
        elif readiness_score >= 70:
            print("   ⚠️  ACCEPTABLE - Functional for production")
        else:
            print("   ❌ NEEDS IMPROVEMENT - Address issues before production")
        
        return readiness_score >= 70
        
    except FileNotFoundError:
        print("❌ Cost validation report not found. Run cost validation first.")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_readiness_check())
    print(f"\n{'✅ READY' if success else '❌ NOT READY'} for production deployment")