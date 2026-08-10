REQ=['mcn_validated','maic_completed','hearing_completed','supports_checked','institutional_responsibility_checked','justifications_checked']
def crps_readiness(checklist,reassessment_required=False):
    req=REQ+(['cycle_comparison_completed'] if reassessment_required else []); miss=[x for x in req if not checklist.get(x)]; return (not miss,miss)
