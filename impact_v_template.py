"""
IMPACT-V scoring template for resume evaluation.
This is used to consistently score candidates across the IMPACT-V framework.
"""

IMPACT_V_TEMPLATE = """
# [Candidate Name] - [Current Role]

## 📊 10-SECOND SCREENING CARD
| Category | Assessment | Score |
|---------|------------|-------|
| 🌍 Location | [Current location & availability summary] | [⚠️/✅/🚫] |
| 💼 Experience | [Years & relevance to target role] | [⭐⭐⭐/⭐⭐/⭐] |
| 🏆 Performance | [Key achievements summary] | [⭐⭐⭐/⭐⭐/⭐] |
| 👥 Leadership | [Team/leadership experience] | [⭐⭐⭐/⭐⭐/⭐] |
| 🔄 Availability | [Relocation/start date issues] | [✅/⚠️/🚫] |
| 📈 Overall | [IMPACT-V Score %] - [One-line assessment] | [⭐⭐⭐(✅/⚠️/🚫)] |

## 💡 VERDICT: **[QUALIFIED/QUALIFIED BUT UNAVAILABLE/NOT QUALIFIED]** - [One-line justification]

## 📊 CAREER TRAJECTORY
[Visual timeline with company progression and notable achievements]

## 🔍 IMPACT-V ASSESSMENT MATRIX

### Industry Fit (0-3)
- ⚙️ Manufacturing sector relationships: [Score] - [Evidence]
- 🍽️ F&B sector relationships: [Score] - [Evidence] 
- 💼 HR/Finance decision-maker access: [Score] - [Evidence]

### Market Knowledge (0-3)
- 🌐 UAE business landscape expertise: [Score] - [Evidence]
- 🏢 Enterprise sales experience in region: [Score] - [Evidence]
- 🗣️ Cultural/language advantages: [Score] - [Evidence]

### Performance Record (0-3)
- 📈 Quantifiable revenue achievements: [Score] - [Evidence]
- 🎯 Consistent target attainment: [Score] - [Evidence]
- 💰 Deal size/complexity comparable to Azine's: [Score] - [Evidence]

### Approach & Solutions (0-3)
- 💳 Financial/SaaS solution sales experience: [Score] - [Evidence]
- 🤝 Consultative selling methodology: [Score] - [Evidence]
- 🔄 Sales process improvement history: [Score] - [Evidence]

### Capability to Lead (0-3)
- 👥 Team building & development: [Score] - [Evidence]
- 📊 Sales operations expertise: [Score] - [Evidence]
- 🔗 Cross-functional collaboration: [Score] - [Evidence]

### Time-to-Value (0-3)
- 🚀 Speed to productivity: [Score] - [Evidence]
- 📱 Existing network leverage: [Score] - [Evidence]
- 🧩 Product knowledge transferability: [Score] - [Evidence]

### Verification Notes
- 📍 Current location & availability: [Assessment]
- ⏱️ Position longevity projections: [RISK LEVEL] - [Evidence]
- 🔎 Reference/achievement verification: [NEEDED/VERIFIED] - [Details]

## 📊 SCORING SUMMARY
- Total IMPACT-V Score: [X/54] ([X]%)
- Critical Categories: [X/Y]
- Readiness Assessment: [Immediate/Short-term/Needs Development/Delayed]

## 💼 FINAL RECOMMENDATION
[Reject/Consider/Strong/Exceptional] - [1-2 sentence justification]

## 🎯 INTERVIEW FOCUS AREAS
- [Key area to probe]
- [Verification needed]
- [Potential concern to address]
"""

def get_scoring_template(role_type="Head of Sales"):
    """
    Return the scoring template customized for the specific role type.
    Future enhancement: customize sections based on role type.
    """
    return IMPACT_V_TEMPLATE 