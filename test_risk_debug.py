#!/usr/bin/env python3
"""
Debug script to test risk assessment logic
"""
from risk_assessment import RiskAssessment
from medical_knowledge import MedicalKnowledgeBase

# Test the exact scenario that should be HIGH risk
test_responses = [
    "Patient: TestUser, Age: 25, Pregnancy Week: 7",
    "no",  # headaches
    "no",  # baby movement
    "no",  # swelling
    "no",  # bleeding
    "140/83",  # blood pressure
    "severe abdominal pain on one side and feel dizzy"  # 6th question
]

print("=== TESTING RISK ASSESSMENT LOGIC ===")
print(f"Test responses: {test_responses}")

# Create risk assessor
knowledge_base = MedicalKnowledgeBase()
risk_assessor = RiskAssessment(knowledge_base)

# Test the assessment
result = risk_assessor.assess_risk(test_responses, 'en')
print(f"\n=== RESULT ===")
print(f"Risk Level: {result.get('risk_level', 'Unknown')}")
print(f"Explanation: {result.get('explanation', 'No explanation')}")
print(f"Recommendations: {result.get('recommendations', 'No recommendations')}")

# Test combined text manually
combined_text = ' '.join(test_responses).lower()
print(f"\n=== MANUAL TEXT ANALYSIS ===")
print(f"Combined text: {combined_text}")

# Test specific keyword detection
ectopic_keywords = ['severe abdominal pain on one side', 'abdominal pain on one side', 'pain on one side']
dizzy_keywords = ['dizzy', 'feel dizzy', 'dizziness']

print(f"\n=== KEYWORD DETECTION ===")
for keyword in ectopic_keywords:
    found = keyword in combined_text
    print(f"'{keyword}' found: {found}")

for keyword in dizzy_keywords:
    found = keyword in combined_text
    print(f"'{keyword}' found: {found}")

# Test the ectopic detection logic
ectopic_pain = any(keyword in combined_text for keyword in ectopic_keywords)
ectopic_dizzy = any(keyword in combined_text for keyword in dizzy_keywords)
ectopic_signs = ectopic_pain and ectopic_dizzy

print(f"\n=== ECTOPIC DETECTION ===")
print(f"Ectopic pain detected: {ectopic_pain}")
print(f"Ectopic dizzy detected: {ectopic_dizzy}")
print(f"Ectopic signs overall: {ectopic_signs}")

print(f"\n=== EXPECTED: HIGH RISK ===")