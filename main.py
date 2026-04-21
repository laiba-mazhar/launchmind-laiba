"""
main.py
LaunchMind — Multi-Agent Startup System
Entry point: runs the full pipeline end-to-end.

Usage:
    python main.py
    python main.py "Your custom startup idea here"
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

# ── Import agents ─────────────────────────────────────────────────────────────
import message_bus as bus
import agents.ceo_agent as ceo
import agents.product_agent as product
import agents.engineer_agent as engineer
import agents.marketing_agent as marketing
import agents.qa_agent as qa


STARTUP_IDEA = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "A mobile app that connects university students with verified local tutors for affordable on-demand sessions"
)


def run():
    print("\n" + "=" * 60)
    print("  LAUNCHMIND — Multi-Agent Startup System")
    print("=" * 60)
    print(f"\n  Idea: {STARTUP_IDEA}\n")

    # ── PHASE 1: CEO decomposes idea ──────────────────────────────────────────
    print("\n── PHASE 1: Task Decomposition ──────────────────────────")
    tasks = ceo.decompose_idea(STARTUP_IDEA)
    ceo.dispatch_to_product(STARTUP_IDEA, tasks["product_focus"])

    # ── PHASE 2: Product agent generates spec ─────────────────────────────────
    print("\n── PHASE 2: Product Specification ───────────────────────")
    spec = product.run()

    # ── FEEDBACK LOOP 1: CEO reviews product spec ─────────────────────────────
    print("\n── FEEDBACK LOOP 1: CEO Reviews Product Spec ────────────")
    revision_count = 0
    while revision_count < ceo.MAX_REVISION_CYCLES:
        review = ceo.review_product_spec(spec, STARTUP_IDEA)
        if review["verdict"] == "pass":
            ceo._log("product", "pass", "proceed_to_build")
            break
        else:
            revision_count += 1
            ceo._log("product", "fail", f"revision_request #{revision_count}", review["feedback"])
            print(f"\n[CEO] Spec rejected (cycle {revision_count}). Requesting revision...")
            ceo.dispatch_revision_to_product(STARTUP_IDEA, review["feedback"])
            spec = product.run(revision_feedback=review["feedback"])
    else:
        print("[CEO] Max revision cycles reached for Product — proceeding anyway.")
        ceo._log("product", "timeout", "proceed_despite_issues")

    print(f"\n[CEO] Product spec accepted: {spec['value_proposition']}")

    # ── PHASE 3: Engineer builds landing page + GitHub ────────────────────────
    print("\n── PHASE 3: Engineer — GitHub + Landing Page ────────────")
    eng_result = engineer.run()
    html = eng_result["html"]
    pr_url = eng_result["pr_url"]
    issue_url = eng_result["issue_url"]

    # ── FEEDBACK LOOP 2: CEO reviews engineer output ──────────────────────────
    print("\n── FEEDBACK LOOP 2: CEO Reviews Engineer Output ─────────")
    eng_revision_count = 0
    while eng_revision_count < ceo.MAX_REVISION_CYCLES:
        eng_review = ceo.review_engineer_output(html, spec)
        if eng_review["verdict"] == "pass":
            ceo._log("engineer", "pass", "html_accepted")
            break
        else:
            eng_revision_count += 1
            ceo._log("engineer", "fail", f"revision_request #{eng_revision_count}", eng_review["feedback"])
            print(f"\n[CEO] HTML rejected (cycle {eng_revision_count}). Requesting revision...")
            # Re-queue task for engineer with revision feedback
            bus.send_message(
                "ceo", "engineer", "revision_request",
                {"spec": spec, "revision_feedback": eng_review["feedback"]},
            )
            eng_result = engineer.run(revision_feedback=eng_review["feedback"])
            html = eng_result["html"]
            pr_url = eng_result["pr_url"]
            issue_url = eng_result["issue_url"]
    else:
        print("[CEO] Max revision cycles reached for Engineer — proceeding.")
        ceo._log("engineer", "timeout", "proceed_despite_issues")

    # ── PHASE 4: Marketing agent ──────────────────────────────────────────────
    print("\n── PHASE 4: Marketing — Email + Slack ───────────────────")
    copy = marketing.run(pr_url=pr_url)

    # ── FEEDBACK LOOP 3: CEO reviews marketing copy ───────────────────────────
    print("\n── FEEDBACK LOOP 3: CEO Reviews Marketing Copy ──────────")
    mkt_review = ceo.review_marketing_output(copy, spec)
    ceo._log(
        "marketing",
        mkt_review["verdict"],
        "copy_accepted" if mkt_review["verdict"] == "pass" else "noted_issues",
        mkt_review.get("feedback", ""),
    )
    # Note: we log the review but don't re-run marketing (email already sent)
    # In a real system you'd gate the Slack post on this review

    # ── PHASE 5: QA agent ─────────────────────────────────────────────────────
    print("\n── PHASE 5: QA Review ───────────────────────────────────")
    ceo.dispatch_to_qa(html, copy, spec, pr_url)
    qa_report = qa.run()

    # ── FEEDBACK LOOP 4: CEO acts on QA verdict ───────────────────────────────
    print("\n── FEEDBACK LOOP 4: CEO Acts on QA Verdict ──────────────")
    if qa_report["overall_verdict"] == "fail":
        html_issues = qa_report["html_review"].get("issues", [])
        copy_issues = qa_report["copy_review"].get("issues", [])

        combined_feedback = (
            "HTML issues: " + "; ".join(i.get("comment", "") for i in html_issues)
            + " | Copy issues: " + "; ".join(copy_issues)
        )
        ceo._log("qa", "fail", "request_engineer_revision", combined_feedback)

        print(f"\n[CEO] QA failed. Requesting final engineer revision...")
        bus.send_message(
            "ceo", "engineer", "revision_request",
            {"spec": spec, "revision_feedback": combined_feedback},
        )
        final_eng = engineer.run(revision_feedback=combined_feedback)
        pr_url = final_eng["pr_url"]
        html = final_eng["html"]
        print(f"[CEO] Final revision committed. PR: {pr_url}")
    else:
        ceo._log("qa", "pass", "no_revisions_needed")
        print("[CEO] QA passed — no further revisions needed.")

    # ── PHASE 6: CEO posts final Slack summary ────────────────────────────────
    print("\n── PHASE 6: Final Slack Summary ─────────────────────────")
    ceo.post_final_summary(STARTUP_IDEA, spec, copy, pr_url, issue_url)

    # ── Print full message log ────────────────────────────────────────────────
    bus.print_full_log()

    # ── Print CEO decision log ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("CEO DECISION LOG")
    print("=" * 60)
    for i, entry in enumerate(ceo.get_decision_log(), 1):
        print(f"[{i}] agent={entry['agent']} | verdict={entry['verdict']} | action={entry['action']}")
        if entry["feedback"]:
            print(f"     feedback: {entry['feedback'][:120]}")

    print("\n" + "=" * 60)
    print("  LAUNCHMIND COMPLETE ✅")
    print(f"  PR:    {pr_url}")
    print(f"  Issue: {issue_url}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run()
